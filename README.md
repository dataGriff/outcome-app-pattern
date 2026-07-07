# outcome-app-pattern

A reference demonstrator for a **source-aligned, API-first, multichannel domain**.

One place owns the behaviour (the API), the data contract, and the events. Multiple
experiences — **web, mobile, and agent** — consume that *same* contract instead of
reimplementing logic. The trivial "generate a colour" example keeps the **pattern**
in focus, not the feature.

## The pattern

```
                         domain/  (the source-aligned core)
                 ┌───────────────────────────────────────────┐
                 │  api/        FastAPI behaviour service     │
                 │  contracts/  AsyncAPI + data contract      │
                 │  events/     event payload schema          │
                 └───────────────────────────────────────────┘
                    ▲ HTTP + SSE            │ colour.generated (CloudEvent)
                    │                       ▼
   experiences/     │              platform/
 ┌───────────┬──────┴─────┐      ┌───────────────────────────────────────┐
 │  web      │  mobile    │      │  streaming/  Benthos: NATS → storage   │
 │  (Flask)  │  (Expo/RN) │      │  storage/    SeaweedFS (S3, data prod) │
 │  agent (MCP server)    │      │  analytics/  Streamlit + pandas        │
 └───────────┴────────────┘      └───────────────────────────────────────┘
     consume the one API              derive the data product from events
```

- **`domain/`** — the one owner of behaviour. `POST /colours` generates a colour, keeps
  recent history, and emits a `colour.generated` CloudEvent to NATS. Read endpoints
  (`GET /colours/latest`, `GET /colours`) and an SSE bridge (`GET /events/stream`)
  give every experience the same live surface. Contracts (AsyncAPI + data contract)
  and the event schema live here too.
- **`experiences/`** — three channels, zero shared code, all consuming the same API +
  event feed: `web` (Flask), `mobile` (Expo/React Native), `agent` (MCP server).
- **`platform/`** — the supporting infrastructure: the streaming pipeline that turns
  events into a durable **data product** in object storage, and the analytics that read
  it back. Operational reads come from the API; analytical reads come from the data
  product — the split is deliberate.

Everything runs locally and in isolation via `docker-compose.yml`. No proprietary
dependencies: the object store is [SeaweedFS](https://github.com/seaweedfs/seaweedfs)
(Apache-2.0).

## Quickstart

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
| Object storage | http://localhost:8888 | SeaweedFS filer UI (data product) |
| Event broker | nats://localhost:4222 | NATS (JetStream) |

Try it: click **Generate** in the web or mobile UI, or `curl -X POST
localhost:8000/colours`. Watch the live feed update in every experience, then see the
event land as a `.jsonl` object in storage and the Streamlit counts move.

## Common tasks

```bash
task ci              # lint contracts + unit + integration tests
task test:unit       # behaviour-service unit tests
task test:mcp        # MCP agent stdio round-trip (needs the API up)
task read:events     # read the data product back into a pandas DataFrame
task gen:client      # generate a typed TS client from the API's OpenAPI
task build:mobile    # build the Expo web-export image (heavy; kept out of ci)
task subscribe:broker  # tail colour.generated events on NATS
```

## Contracts & events

- **API events** — `domain/contracts/api/behaviour-service.asyncapi.yaml` (AsyncAPI)
- **Data product** — `domain/contracts/data/data-product.contract.yaml` (Data Contract)
- **Event payload** — `domain/events/colour.generated.schema.json` (JSON Schema, CloudEvents)

Contract-first: the integration test validates emitted events against the AsyncAPI
schema, and `task gen:client` derives the experiences' client from the same API spec —
so behaviour, events, and clients cannot drift from the contracts.
