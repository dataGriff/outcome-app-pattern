from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import random
import asyncio
import uuid

from nats.aio.client import Client as NATS
from cloudevents.http import CloudEvent
import os

app = FastAPI()

class Colour(str, Enum):
    red = "red"
    amber = "amber"
    green = "green"

class ColourEvent(BaseModel):
    colour: Colour
    timestamp: datetime

async def publish_cloudevent(event: ColourEvent):
    nc = NATS()
    await nc.connect(os.getenv("NATS_URL", "nats://localhost:4222"))
    attributes = {
        "id": str(uuid.uuid4()),
        "source": "urn:outcome-app-pattern:behaviour-service",
        "specversion": "1.0",
        "type": "colour.generated",
        "time": event.timestamp.isoformat(),
    }
    data = {"colour": event.colour, "timestamp": event.timestamp.isoformat()}
    ce = CloudEvent(attributes, data)
    headers, body = ce.MarshalJson()
    # Publish to NATS subject 'colour.generated'
    await nc.publish("colour.generated", body)
    await nc.drain()

@app.post("/generate-colour", response_model=ColourEvent)
def generate_colour():
    colour = random.choice(list(Colour))
    event = ColourEvent(colour=colour, timestamp=datetime.utcnow())
    # Publish CloudEvent asynchronously
    asyncio.create_task(publish_cloudevent(event))
    return event
