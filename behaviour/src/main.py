from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
import random

app = FastAPI()

class Colour(str, Enum):
    red = "red"
    amber = "amber"
    green = "green"

class ColourEvent(BaseModel):
    colour: Colour
    timestamp: datetime

@app.post("/generate-colour", response_model=ColourEvent)
def generate_colour():
    colour = random.choice(list(Colour))
    event = ColourEvent(colour=colour, timestamp=datetime.utcnow())
    # TODO: Emit CloudEvent here
    return event
