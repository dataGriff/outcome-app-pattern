"""Operational store (Postgres) for the behaviour domain.

The API's durable state and its transactional outbox live here. Writing the
colour and the outbox row in one transaction is what lets the relay ship events
without a dual-write to NATS inside the request.
"""
import json
import os

import asyncpg

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://colour:colour@operational-store:5432/colour"
)

_pool: asyncpg.Pool | None = None


async def connect():
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL)


async def close():
    if _pool is not None:
        await _pool.close()


async def create_colour(colour: str, build_event):
    """Insert the colour and its outbox event in one transaction.

    ``build_event(colour, created_at)`` returns the CloudEvent dict to enqueue;
    it is called with the DB-assigned timestamp so the event time and the
    operational row share one clock.
    """
    async with _pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "INSERT INTO colours (colour) VALUES ($1) "
                "RETURNING colour, created_at",
                colour,
            )
            event = build_event(row["colour"], row["created_at"])
            await conn.execute(
                "INSERT INTO outbox (subject, payload) VALUES ($1, $2::jsonb)",
                event["type"],
                json.dumps(event),
            )
    return row


async def latest():
    async with _pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT colour, created_at FROM colours "
            "ORDER BY created_at DESC, id DESC LIMIT 1"
        )


async def recent(limit: int):
    async with _pool.acquire() as conn:
        return await conn.fetch(
            "SELECT colour, created_at FROM colours "
            "ORDER BY created_at DESC, id DESC LIMIT $1",
            limit,
        )
