import os

import httpx
from mcp.server.fastmcp import FastMCP

API = os.getenv("DOMAIN_API_URL", "http://localhost:8000")
TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")

mcp = FastMCP("colour-domain", host="0.0.0.0", port=3001)


@mcp.tool()
async def generate_colour() -> dict:
    """Generate a new colour event via the behaviour domain (POST /colours)."""
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API}/colours", timeout=5)
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def latest_colour() -> dict:
    """Return the most recently generated colour (GET /colours/latest)."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API}/colours/latest", timeout=5)
        if r.status_code == 404:
            return {"detail": "no colours generated yet"}
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def colour_history(limit: int = 10) -> list:
    """Return recent colour history, most recent first (GET /colours?limit=N)."""
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API}/colours", params={"limit": limit}, timeout=5)
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    mcp.run(transport=TRANSPORT)
