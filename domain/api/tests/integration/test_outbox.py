"""Integration: POST → colours row + outbox row → relay publishes → row marked.

Proves the transactional-outbox path end to end against real Postgres and the
running relay. Runs inside the compose contract-test container.
"""
import asyncio
import os

import asyncpg
import requests

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://colour:colour@postgres:5432/colour"
)
API = os.getenv("DOMAIN_API_URL", "http://behaviour-service:8000")


async def run():
    conn = await asyncpg.connect(DATABASE_URL)

    before = await conn.fetchval("SELECT count(*) FROM colours")
    resp = requests.post(f"{API}/colours")
    assert resp.status_code == 200, resp.text

    # Operational row written.
    after = await conn.fetchval("SELECT count(*) FROM colours")
    assert after == before + 1, "colour was not persisted operationally"

    # Outbox row written and drained by the relay (published_at set).
    published = None
    for _ in range(20):
        published = await conn.fetchval(
            "SELECT count(*) FROM outbox WHERE published_at IS NOT NULL"
        )
        unpublished = await conn.fetchval(
            "SELECT count(*) FROM outbox WHERE published_at IS NULL"
        )
        if unpublished == 0 and published > 0:
            break
        await asyncio.sleep(0.5)

    assert published and published > 0, "relay did not drain the outbox"
    await conn.close()
    print("Outbox round-trip OK")


if __name__ == "__main__":
    asyncio.run(run())
