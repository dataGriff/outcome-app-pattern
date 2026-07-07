"""Outbox relay: drain unpublished outbox rows to NATS.

Polls the outbox, publishes each payload to its subject, and marks it sent —
all while holding the row lock (FOR UPDATE SKIP LOCKED), so delivery is
at-least-once and safe to run as a single replica. This is the component that
turns the transactional write into an emitted event without a dual-write.
"""
import asyncio
import os

import asyncpg
from nats.aio.client import Client as NATS

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://colour:colour@operational-store:5432/colour"
)
EVENT_BROKER_URL = os.getenv("EVENT_BROKER_URL", "nats://events:4222")
POLL_SECONDS = float(os.getenv("RELAY_POLL_SECONDS", "0.5"))
BATCH = int(os.getenv("RELAY_BATCH", "50"))


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


async def main():
    pool = await asyncpg.create_pool(DATABASE_URL)
    nc = NATS()
    await nc.connect(EVENT_BROKER_URL)
    print(f"Relay up: operational-store + event broker {EVENT_BROKER_URL}")
    while True:
        published = await drain(pool, nc)
        if published:
            print(f"Published {published} event(s)")
        else:
            await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
