# outcome-app-pattern

A reference demonstrator for a **source-aligned, API-first, multichannel domain**.

One place owns the behaviour (the API), the operational state, the data contract, and
the events. Multiple experiences — **web, mobile, and agent** — consume that *same*
contract instead of reimplementing logic. The trivial "generate a colour" example keeps
the **pattern** in focus, not the feature.

## The pattern

```
                              domain/  (the source-aligned core)
        ┌──────────────────────────────────────────────────────────────────┐
        │  api/        FastAPI behaviour service                            │
        │  contracts/  OpenAPI (HTTP) + AsyncAPI (events) + data contracts  │
        │  events/     event payload schema                                 │
        │  relay/      outbox relay                                         │
        │                                                                  │
        │   POST /colours ─┐                                               │
        │                  ▼   one transaction                            │
        │            ┌───────────────┐   outbox rows   ┌─────────┐        │
        │            │  Postgres     │────────────────▶│  relay  │──┐     │
        │            │  colours+outbox│  (operational)  └─────────┘  │     │
        │            └───────────────┘                              │     │
        └──────────────────────────────────────────────────────────┼─────┘
                     ▲ HTTP reads / SSE                              ▼ colour.generated
                     │                                          ┌────────┐
   experiences/      │                                          │  NATS  │
 ┌───────────┬───────┴────┐                                     └───┬────┘
 │  web      │  mobile    │◀──── SSE bridge (API) ◀──────────────────┤
 │  (Flask)  │  (Expo/RN) │                                          │
 │  agent (MCP server)    │                            platform/     ▼
 └───────────┴────────────┘                     ┌──────────────────────────────────┐
   consume the one API                          │ streaming/  bento: NATS → storage │
                                                │ storage/    SeaweedFS (S3)        │
                                                │   colour-operational/  (raw JSONL)│
                                                │   colour-performance/  (Parquet)  │
                                                │ analytics/  summariser + Streamlit│
                                                └──────────────────────────────────┘
```

- **`domain/`** — the one owner of behaviour. `POST /colours` generates a colour and, **in a
  single Postgres transaction**, writes both the operational row and a transactional **outbox**
  row. The **relay** ships the outbox to NATS — no dual-write inside the request. Read endpoints
  (`GET /colours/latest`, `GET /colours`) are served from Postgres, and an SSE bridge
  (`GET /events/stream`) gives every experience the same live surface. All three contracts
  (OpenAPI, AsyncAPI, data) and the event schema live here too.
- **`experiences/`** — three channels, zero shared code, all consuming the same API + event
  feed: `web` (Flask), `mobile` (Expo/React Native), `agent` (MCP server).
- **`platform/`** — the supporting infrastructure. bento streams events to object storage; the
  **summariser** rolls the raw stream up into a curated daily aggregate; analytics read the
  products back.

**Operational vs analytical, demonstrated (not asserted):** live reads come from the domain API
(Postgres); historical/aggregate reads come from the **data products in SeaweedFS**. The raw
product is append-only JSONL; the curated daily aggregate is columnar Parquet.

Everything runs locally and in isolation via `docker-compose.yml`. No proprietary dependencies:
the object store is [SeaweedFS](https://github.com/seaweedfs/seaweedfs) (Apache-2.0).

**Taking the pattern elsewhere:** [docs/replication.md](docs/replication.md) is the lift-out guide
(zones, order of work, naming rules, and the exact domain-specific touchpoints to swap);
[docs/productionising.md](docs/productionising.md) lists what the demo deliberately omits and what
to add before production.

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
| Object storage | http://localhost:8888 | SeaweedFS filer UI (data products) |
| Operational store | localhost:5433 | Postgres (colours + outbox) |
| Event broker | nats://localhost:4222 | NATS (JetStream) |

Try it: click **Generate** in the web or mobile UI, or `curl -X POST localhost:8000/colours`.
Watch the live feed update in every experience, then see the event land as a `.jsonl` object
under `colour-operational/`, the summariser roll it into `colour-performance/`, and the
Streamlit counts move.

## Common tasks

```bash
task ci                 # lint all 3 contracts + unit, runtime-conformance, data-product tests
task test:unit          # behaviour-service unit tests (hermetic)
task test:integration   # runtime conformance: AsyncAPI events + outbox round-trip + OpenAPI (Schemathesis + spec drift)
task test:contract:data # test both data-product contracts against storage (needs the stack up)
task summarise:daily    # run the daily summariser once
task read:events        # read the raw data product back into a pandas DataFrame
task gen:client         # generate a typed TS client from the committed OpenAPI contract
task build:mobile       # build the Expo web-export image (heavy; kept out of ci)
task subscribe:broker   # tail colour.generated events on NATS
```

## Contracts & events

Three authored, versioned, **verified** contracts — the API cannot drift from any of them:

- **HTTP API** — `domain/contracts/api/behaviour-service.openapi.yaml` (OpenAPI). Source of truth
  for the HTTP surface; the implementation is checked against it with Schemathesis plus a
  spec-drift test (the served `/openapi.json` must not drift from the committed contract), and the
  mobile experience consumes it through a typed client generated from it (`task gen:client`).
- **Events** — `domain/contracts/api/behaviour-service.asyncapi.yaml` (AsyncAPI). Emitted events
  are validated against it in the integration test.
- **Data products** — named for the need they serve, not their shape:
  `domain/contracts/data/colour-operational.contract.yaml` (**operational awareness** + long-term
  granular detail; raw JSONL) and `domain/contracts/data/colour-performance.contract.yaml`
  (**performance** over time + current status; curated Parquet). Each contract states its purpose,
  and both are verified against the real objects in SeaweedFS with `datacontract test`. The
  Streamlit app has a tab per product: **Operational Awareness** and **Performance**.
- **Event payload** — `domain/events/colour.generated.schema.json` (JSON Schema, CloudEvents).

## Notes & caveats

- **At-least-once delivery.** The outbox relay marks a row published only after the NATS publish
  succeeds, holding the row lock (`FOR UPDATE SKIP LOCKED`). A crash between publish and mark can
  redeliver — consumers should be idempotent. Run a single relay replica. The relay prunes
  published rows older than `OUTBOX_RETENTION_SECONDS` (default 1h) — the outbox is a delivery
  log, not history.
- **Single-node demo.** One relay, one API replica, in-process SSE fan-out. The durability story
  is Postgres (operational) and SeaweedFS (analytical), not horizontal scale.
- **Throwaway credentials.** `platform/storage/s3.json` commits a fixed demo S3 key — safe only
  because this is a local, disposable demo. The host Postgres port is `5433` and the web UI is on
  `5001` to avoid common local conflicts (5432, macOS AirPlay on 5000).
