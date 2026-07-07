"""Daily summariser: roll the colour-operational events up into the
colour-performance curated data product.

Reads the flat JSONL operational product, groups by day + colour, counts, and
writes Parquet (the curated analytical format). Full recompute → overwrite a
single object; deterministic and fine at demo scale. This is the routine batch
rollup most apps need, made explicit.
"""
import io
import json
import logging
import os
import time

import boto3
import pandas as pd

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://object-storage:8333")
BUCKET = os.getenv("BUCKET", "mybucket")
RAW_PREFIX = "colour-operational/"
AGG_KEY = "colour-performance/colour-performance.parquet"
INTERVAL = int(os.getenv("SUMMARISE_INTERVAL_SECONDS", "0"))  # 0 = run once

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("summariser")


def _client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "demokey"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "demosecret"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )


def _read_raw(s3) -> pd.DataFrame:
    objects = s3.list_objects_v2(Bucket=BUCKET, Prefix=RAW_PREFIX).get("Contents", [])
    rows = []
    for obj in objects:
        if not obj["Key"].endswith(".jsonl"):
            continue
        body = s3.get_object(Bucket=BUCKET, Key=obj["Key"])["Body"].read().decode()
        for line in body.splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)


def summarise_once():
    s3 = _client()
    raw = _read_raw(s3)
    if raw.empty:
        logger.info("No raw events yet; nothing to summarise.")
        return

    raw["date"] = pd.to_datetime(raw["timestamp"]).dt.strftime("%Y-%m-%d")
    agg = (
        raw.groupby(["date", "colour"])
        .size()
        .reset_index(name="count")
        .astype({"count": "int64"})
    )

    buf = io.BytesIO()
    agg.to_parquet(buf, index=False)
    s3.put_object(Bucket=BUCKET, Key=AGG_KEY, Body=buf.getvalue())
    logger.info("Wrote %d aggregate row(s) to %s", len(agg), AGG_KEY)


def main():
    if INTERVAL <= 0:
        summarise_once()
        return
    while True:
        try:
            summarise_once()
        except Exception:  # keep the loop alive in the demo
            logger.exception("Summarise run failed")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
