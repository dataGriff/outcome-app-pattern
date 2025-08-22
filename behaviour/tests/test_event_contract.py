import asyncio
import json
import yaml
from nats.aio.client import Client as NATS
from jsonschema import validate
import requests

# Load AsyncAPI spec and extract the ColourGeneratedEvent schema
def get_event_schema():
    with open("contracts/api/behaviour-service.asyncapi.yaml") as f:
        asyncapi = yaml.safe_load(f)
    return asyncapi["components"]["messages"]["ColourGeneratedEvent"]["payload"]

# Test function to POST to API and check event on NATS
def test_colour_generated_event():
    schema = get_event_schema()
    received_event = None
    nc = None

    async def nats_subscribe():
        nonlocal received_event
        nonlocal nc
        nc = NATS()
        await nc.connect("nats://event-hub:4222")
        async def cb(msg):
            nonlocal received_event
            received_event = json.loads(msg.data.decode())
        await nc.subscribe("colour.generated", cb=cb)

    async def run_test():
        await nats_subscribe()
        # Give NATS a moment to subscribe
        await asyncio.sleep(1)
        # Trigger the API
        resp = requests.post("http://behaviour-service:8000/generate-colour")
        assert resp.status_code == 200
        # Wait for event
        for _ in range(10):
            if received_event:
                break
            await asyncio.sleep(0.5)
        assert received_event is not None, "No event received from NATS"
        # Validate event against schema
        validate(instance=received_event, schema=schema)
        print("Event matches AsyncAPI contract!")
        if nc is not None:
            await nc.close()

    asyncio.run(run_test())

if __name__ == "__main__":
    test_colour_generated_event()
