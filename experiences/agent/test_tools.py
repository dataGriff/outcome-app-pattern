"""Smoke-test the MCP tools over stdio against a running behaviour API.

Requires the behaviour service reachable at DOMAIN_API_URL (default
http://localhost:8000). Spawns server.py over stdio and exercises each tool.
"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("tools:", names)
            assert {"generate_colour", "latest_colour", "colour_history"} <= set(names)

            gen = await session.call_tool("generate_colour", {})
            print("generate_colour ->", gen.content[0].text)

            latest = await session.call_tool("latest_colour", {})
            print("latest_colour ->", latest.content[0].text)

            hist = await session.call_tool("colour_history", {"limit": 3})
            print("colour_history ->", hist.content[0].text)

    print("MCP round-trip OK")


if __name__ == "__main__":
    asyncio.run(main())
