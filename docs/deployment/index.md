# Deployment

Everything runs locally and in isolation via `docker-compose.yml`. There are no proprietary
dependencies — the object store is [SeaweedFS](https://github.com/seaweedfs/seaweedfs)
(Apache-2.0).

## Run the stack

```bash
task up          # build + start the whole stack
```

| Channel / service | URL | What it is |
| --- | --- | --- |
| Behaviour API | http://localhost:8000/docs | The one domain API (OpenAPI docs) |
| Web experience | http://localhost:5001 | Flask UI — generate + live SSE feed |
| Mobile experience | http://localhost:8081 | Expo/RN web export — same API + feed |
| Agent experience | http://localhost:3001/mcp | MCP server (tools over streamable-http) |
| Analytics | http://localhost:8501 | Streamlit charts over the data product |
| Object storage | http://localhost:8888 | SeaweedFS filer UI (data products) |
| Operational store | localhost:5433 | Postgres (colours + outbox) |
| Event broker | nats://localhost:4222 | NATS (JetStream) |

Try it: click **Generate** in the web or mobile UI, or `curl -X POST localhost:8000/colours`.
Watch the live feed update in every experience, then see the event land as a `.jsonl` object
under `colour-operational/`, the summariser roll it into `colour-performance/`, and the
Streamlit counts move.

The host Postgres port is `5433` and the web UI is on `5001` to avoid common local conflicts
(5432, macOS AirPlay on 5000).

## This is a single-node demo

By design — one relay, one API replica, in-process SSE fan-out, single-node volumes. The
durability story is Postgres (operational) and SeaweedFS (analytical), not horizontal scale.
Everything to add before running for real is in [productionising](../productionising/index.md).
For running the pattern on a different platform entirely, see
[replication](../replication/index.md).
