"""Outbox relay: drain unpublished outbox rows to NATS.

Polls the outbox, publishes each payload to its subject, and marks it sent —
all while holding the row lock (FOR UPDATE SKIP LOCKED), so delivery is
at-least-once and safe to run as a single replica. This is the component that
turns the transactional write into an emitted event without a dual-write.
"""
import asyncio
import logging
import os
import time

import asyncpg
from nats.aio.client import Client as NATS

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://colour:colour@operational-store:5432/colour"
)
EVENT_BROKER_URL = os.getenv("EVENT_BROKER_URL", "nats://events:4222")
POLL_SECONDS = float(os.getenv("RELAY_POLL_SECONDS", "0.5"))
BATCH = int(os.getenv("RELAY_BATCH", "50"))
PRUNE_INTERVAL_SECONDS = float(os.getenv("OUTBOX_PRUNE_INTERVAL_SECONDS", "60"))
RETENTION_SECONDS = float(os.getenv("OUTBOX_RETENTION_SECONDS", "3600"))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("outbox-relay")


async def drain(pool, nc) -> int:
    async with pool.acquire() as conn:
        async with conn.transaction():
            rows = await conn.fetch(
                "SELECT id, subject, payload::text AS payload FROM outbox "
                "WHERE published_at IS NULL "
                "ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT $1",
                BATCH,
            )
            for r in rows:
                await nc.publish(r["subject"], r["payload"].encode())
                await conn.execute(
                    "UPDATE outbox SET published_at = now() WHERE id = $1", r["id"]
                )
            if rows:
                await nc.flush()
    return len(rows)


async def prune(pool) -> int:
    # Published rows are a delivery log, not history — the operational table
    # and the data products hold the record. Prune so the outbox stays bounded.
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM outbox WHERE published_at < now() - make_interval(secs => $1)",
            RETENTION_SECONDS,
        )
    return int(result.split()[-1])


async def main():
    pool = await asyncpg.create_pool(DATABASE_URL)
    nc = NATS()
    await nc.connect(EVENT_BROKER_URL)
    logger.info("Relay up: operational-store + event broker %s", EVENT_BROKER_URL)
    last_prune = time.monotonic()
    while True:
        published = await drain(pool, nc)
        if published:
            logger.info("Published %d event(s)", published)
        else:
            await asyncio.sleep(POLL_SECONDS)
        if time.monotonic() - last_prune >= PRUNE_INTERVAL_SECONDS:
            pruned = await prune(pool)
            if pruned:
                logger.info("Pruned %d published outbox row(s)", pruned)
            last_prune = time.monotonic()


if __name__ == "__main__":
    asyncio.run(main())
