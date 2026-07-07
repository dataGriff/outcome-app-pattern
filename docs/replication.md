# Replicating this pattern for your own domain

This repo demonstrates a **source-aligned, API-first, multichannel domain**. The colour
example is deliberately trivial — everything except the word "colour" is the pattern.
This guide is the lift-out: what each zone owns, the order to build in, the naming rules,
and exactly what to swap for your domain.

## The three zones

| Zone | Owns | Rule |
| --- | --- | --- |
| `domain/` | The behaviour API, the operational store schema, the outbox relay, **all contracts** (OpenAPI, AsyncAPI, data), the event schema | One owner for behaviour and every contract. Nothing else defines what the domain means. |
| `experiences/` | One directory per channel (web, mobile, agent, …) | Channels consume the one API + event feed. Zero shared code between channels; no domain logic in any of them. |
| `platform/` | Streaming (broker → storage), storage init, analytics (summariser, visualisation) | Infrastructure and analytical consumers. Reads data products, never the operational store. |

## Order of work

Contract-first, in this order (the same order used to build this repo — see
`.github/instructions/development.instructions.md`):

1. **Contracts** — author the OpenAPI spec, the AsyncAPI spec, and one data contract per
   data product *before* implementation. Lint them (`task lint:all`).
2. **Infrastructure** — compose services for the operational store, event broker, object
   storage. Role-name them (see below).
3. **Behaviour** — the API + operational schema + transactional outbox + relay. Verify
   against the contracts: Schemathesis conformance, the spec-drift test, and the event
   contract test.
4. **Data products** — streaming pipeline for the raw product, batch summariser for the
   curated product. Verify with `datacontract test` against real objects.
5. **Experiences** — one channel at a time, each consuming the API (typed client generated
   from the committed OpenAPI spec: `task gen:client`).
6. **CI** — everything above runs through one `task ci`, so agents, developers, and CI
   execute the identical commands.

## Naming rules

- **Role-name infrastructure services** — the compose service says what it *is for*, not
  the product: `events` (not `nats`), `operational-store` (not `postgres`),
  `object-storage` (not `seaweedfs`), `streaming` (not `bento`). Swapping the
  implementation later doesn't ripple through configs.
- **Keep honest implementation names** where they are protocols, standards, or image
  contracts: `nats://`, `postgresql://`, `s3://`, `AWS_*`/`S3_ENDPOINT` (the S3 standard),
  `POSTGRES_*` (the image's contract), the image tags themselves.
- **Purpose-name data products** — name them for the need they serve, not their shape:
  `colour-operational` (operational awareness + long-term detail), `colour-performance`
  (performance over time + current status). Each data contract states its purpose, and the
  analytics UI gives each product its own surface (a tab per product).
- **Config keys are role-generic** — `EVENT_BROKER_URL`, `DATABASE_URL`, `DOMAIN_API_URL`.

## What is domain-specific (the rename checklist)

Everything below is the "colour" domain; the rest of the repo is scaffolding. To stand up
a new domain (say `dogs` with a `dog.listed` event), replace each touchpoint class:

| Touchpoint | Where |
| --- | --- |
| Resource + endpoints (`/colours`, `/colours/latest`) | `domain/contracts/api/*.openapi.yaml`, `domain/api/src/main.py`, every experience |
| Event subject + type (`colour.generated`) | `main.py` (`SUBJECT`), AsyncAPI contract, `domain/events/*.schema.json`, streaming input, `subscribe:broker` task |
| Operational schema (`colours` table; the `outbox` table is scaffolding — keep it) | `platform/storage/init/*.sql`, `domain/api/src/db.py` |
| DB name/user (`colour`) | compose `POSTGRES_*` + every `DATABASE_URL` |
| Data-product names + prefixes (`colour-operational/`, `colour-performance/`) | data contracts, streaming output path, summariser, visualisation, `read_events_to_df.py` |
| Contract ids (`urn:outcome-app-pattern:*`) | all contracts, `main.py` (`SOURCE`) |
| Domain vocabulary (the colour enum, `ColourEvent`) | OpenAPI/AsyncAPI/data contract schemas, `main.py` models, experiences' rendering |

A grep for `colour` finds every instance; the classes above tell you what each one is.

## What is scaffolding (copy unchanged)

The transactional outbox + relay, the SSE bridge, the contract test harness (Schemathesis,
spec-drift, event contract, `datacontract test`), the compose healthcheck/`--wait` setup,
the Taskfile shape, and the CI workflow. These carry the pattern; they don't know about
colours beyond configuration.

## Before production

This is a local, single-node demo by design. See [productionising.md](productionising.md)
for the explicit list of what to add before running the pattern in production.
