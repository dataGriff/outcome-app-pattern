import os
import asyncio
import json
from nats.aio.client import Client as NATS
import pandas as pd
from deltalake.writer import write_deltalake

# MinIO/S3 config
os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"
os.environ["AWS_REGION"] = "us-east-1"
S3_ENDPOINT = "http://minio:9000"
BUCKET = "mybucket"
DELTA_PATH = f"s3://{BUCKET}/events-delta-table"

# NATS config
NATS_URL = "nats://event-hub:4222"
SUBJECT = "events"

async def main():
    nc = NATS()
    await nc.connect(servers=[NATS_URL])
    print(f"Connected to NATS at {NATS_URL}")

    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        print(f"Received message: {data}")
        df = pd.DataFrame([data])
        # Write or append to Delta table on MinIO
        write_deltalake(
            DELTA_PATH,
            df,
            mode="append",
            storage_options={
                "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
                "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
                "AWS_REGION": os.environ["AWS_REGION"],
                "endpoint_url": S3_ENDPOINT,
            },
        )
        print("Written to Delta table.")

    await nc.subscribe(SUBJECT, cb=message_handler)
    print(f"Subscribed to subject: {SUBJECT}")
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
