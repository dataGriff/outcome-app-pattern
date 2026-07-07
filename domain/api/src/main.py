import asyncio
import json
import os
import random
import uuid
from collections import deque
from datetime import datetime
from enum import Enum
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from nats.aio.client import Client as NATS
from cloudevents.http import CloudEvent, to_structured

SUBJECT = "colour.generated"
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")

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


# Operational state: recent history is kept in-memory (single-replica demo).
# Durable/analytical history is the data product in object storage.
_history: "deque[ColourEvent]" = deque(maxlen=100)

# Per-connection SSE queues, fed by the long-lived NATS subscription below.
_subscribers = set()


async def publish_cloudevent(event: ColourEvent):
    nc = NATS()
    await nc.connect(NATS_URL)
    attributes = {
        "id": str(uuid.uuid4()),
        "source": "urn:outcome-app-pattern:behaviour-service",
        "specversion": "1.0",
        "type": SUBJECT,
        "time": event.timestamp.isoformat(),
    }
    data = {"colour": event.colour, "timestamp": event.timestamp.isoformat()}
    ce = CloudEvent(attributes, data)
    headers, body = to_structured(ce)
    await nc.publish(SUBJECT, body)
    await nc.drain()


@app.on_event("startup")
async def _bridge_events_to_sse():
    """One long-lived NATS subscription fans colour.generated out to SSE clients.

    NATS is not browser-native, so this bridge is what lets web, mobile and
    agent experiences all consume the same live event feed over plain HTTP.
    """
    nc = NATS()
    try:
        await nc.connect(NATS_URL)
    except Exception:
        # Broker not up (e.g. unit tests / API-only run) — SSE stays quiet.
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
async def _close_nats():
    nc = getattr(app.state, "nats", None)
    if nc is not None:
        await nc.drain()


async def _generate() -> ColourEvent:
    colour = random.choice(list(Colour))
    event = ColourEvent(colour=colour, timestamp=datetime.utcnow())
    _history.append(event)
    await publish_cloudevent(event)
    return event


@app.post("/colours", response_model=ColourEvent)
async def create_colour():
    return await _generate()


@app.post("/generate-colour", response_model=ColourEvent)
async def generate_colour():
    """Back-compat alias for POST /colours."""
    return await _generate()


@app.get("/colours/latest", response_model=ColourEvent)
async def latest_colour():
    if not _history:
        raise HTTPException(status_code=404, detail="no colours generated yet")
    return _history[-1]


@app.get("/colours", response_model=List[ColourEvent])
async def colour_history(limit: int = 10):
    return list(reversed(list(_history)))[:limit]


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
