import asyncio
import json
import os
import random
import uuid
from datetime import datetime
from enum import Enum
from typing import List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from nats.aio.client import Client as NATS

try:  # flat layout inside the container (WORKDIR /app), packaged layout in tests
    import db
except ImportError:  # pragma: no cover
    from domain.api.src import db

SUBJECT = "colour.generated"
SOURCE = "urn:outcome-app-pattern:behaviour-service"
EVENT_BROKER_URL = os.getenv("EVENT_BROKER_URL", "nats://localhost:4222")

app = FastAPI(title="Colour Behaviour Service")

# Experiences (mobile web export, agents) call the API cross-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Colour(str, Enum):
    red = "red"
    amber = "amber"
    green = "green"


class ColourEvent(BaseModel):
    colour: Colour
    timestamp: datetime


# Per-connection SSE queues, fed by the long-lived NATS subscription below.
_subscribers = set()


def _build_event(colour: str, ts: datetime) -> dict:
    """Structured CloudEvent for the outbox / NATS. Kept as a plain dict so we
    depend on nothing fragile to serialise it."""
    return {
        "id": str(uuid.uuid4()),
        "source": SOURCE,
        "specversion": "1.0",
        "type": SUBJECT,
        "time": ts.isoformat(),
        "data": {"colour": colour, "timestamp": ts.isoformat()},
    }


@app.on_event("startup")
async def _startup():
    # Operational store is required — fail loudly in real runs if it's absent.
    await db.connect()
    await _bridge_events_to_sse()


async def _bridge_events_to_sse():
    """One long-lived NATS subscription fans colour.generated out to SSE clients.

    NATS is not browser-native, so this bridge is what lets web, mobile and
    agent experiences all consume the same live event feed over plain HTTP.
    """
    nc = NATS()
    try:
        await nc.connect(EVENT_BROKER_URL)
    except Exception:
        # Broker not up (e.g. API-only run) — SSE stays quiet.
        return
    app.state.nats = nc

    async def _on_message(msg):
        try:
            event = json.loads(msg.data.decode())
        except (ValueError, UnicodeDecodeError):
            return
        payload = event.get("data", event)
        for q in list(_subscribers):
            q.put_nowait(payload)

    await nc.subscribe(SUBJECT, cb=_on_message)


@app.on_event("shutdown")
async def _shutdown():
    nc = getattr(app.state, "nats", None)
    if nc is not None:
        await nc.drain()
    await db.close()


async def _generate() -> ColourEvent:
    colour = random.choice(list(Colour))
    row = await db.create_colour(colour.value, _build_event)
    return ColourEvent(colour=row["colour"], timestamp=row["created_at"])


@app.post("/colours", response_model=ColourEvent)
async def create_colour():
    return await _generate()


@app.post("/generate-colour", response_model=ColourEvent)
async def generate_colour():
    """Back-compat alias for POST /colours."""
    return await _generate()


@app.get("/colours/latest", response_model=ColourEvent)
async def latest_colour():
    row = await db.latest()
    if row is None:
        raise HTTPException(status_code=404, detail="no colours generated yet")
    return ColourEvent(colour=row["colour"], timestamp=row["created_at"])


@app.get("/colours", response_model=List[ColourEvent])
async def colour_history(limit: int = Query(10, ge=1, le=100)):
    rows = await db.recent(limit)
    return [ColourEvent(colour=r["colour"], timestamp=r["created_at"]) for r in rows]


@app.get("/events/stream")
async def events_stream():
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.add(q)

    async def event_generator():
        try:
            while True:
                payload = await q.get()
                yield f"data: {json.dumps(payload)}\n\n"
        finally:
            _subscribers.discard(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
