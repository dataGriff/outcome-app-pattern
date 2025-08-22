import os
import asyncio
import json
import uuid
from nats.aio.client import Client as NATS
import boto3
from botocore.client import Config

# MinIO/S3 config
os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"
os.environ["AWS_REGION"] = "us-east-1"
S3_ENDPOINT = "http://minio:9000"
BUCKET = "mybucket"
JSON_OBJECT_PREFIX = "events-json-stream/"

# NATS config
NATS_URL = "nats://event-hub:4222"
SUBJECT = "colour.generated"

# Set up S3 client for MinIO
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_REGION"],
    config=Config(signature_version="s3v4"),
)

def write_event_to_minio(event_dict):
    guid = str(uuid.uuid4())
    object_key = f"{JSON_OBJECT_PREFIX}{guid}.jsonl"
    body = json.dumps(event_dict) + "\n"
    s3.put_object(Bucket=BUCKET, Key=object_key, Body=body.encode())
    print(f"Wrote event to {object_key}")

async def main():
    nc = NATS()
    await nc.connect(servers=[NATS_URL])
    print(f"Connected to NATS at {NATS_URL}")

    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            print(f"Received message: {data}")
            write_event_to_minio(data)
        except Exception as e:
            print(f"Error processing message: {e}")

    await nc.subscribe(SUBJECT, cb=message_handler)
    print(f"Subscribed to subject: {SUBJECT}")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
