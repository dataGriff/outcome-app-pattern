# experiences/agent — MCP server experience

The **agent** channel: an [MCP](https://modelcontextprotocol.io) server that
exposes the one behaviour domain as agent tools, so Claude (or any MCP host) is
just another consumer of the same API as web and mobile.

Tools (thin wrappers over the API at `DOMAIN_API_URL`):

| Tool | API call |
| --- | --- |
| `generate_colour()` | `POST /colours` |
| `latest_colour()` | `GET /colours/latest` |
| `colour_history(limit)` | `GET /colours?limit=N` |

## Local use (stdio) — the normal MCP pattern

An agent host spawns the server over stdio. Add to `.mcp.json` (or Claude
Desktop config), with the behaviour API running on its published port:

```json
{
  "mcpServers": {
    "colour-domain": {
      "command": "python3",
      "args": ["experiences/agent/server.py"],
      "env": { "DOMAIN_API_URL": "http://localhost:8000" }
    }
  }
}
```

Smoke-test the round-trip (needs the behaviour API up):

```bash
cd experiences/agent
pip install -r requirements.txt
DOMAIN_API_URL=http://localhost:8000 python3 test_tools.py
```

## In the demo (compose)

`docker-compose.yml` also runs the server over HTTP (`streamable-http` on
port 3001) so `task up` shows all three experiences live at once. This is a demo
convenience; the canonical usage is stdio from an agent host.
