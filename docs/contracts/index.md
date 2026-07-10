# Contracts

Three authored, versioned, **verified** contracts plus the event payload schema — the API
cannot drift from any of them. Contracts are authored and linted *before* the implementation
they describe (see [development](../development/index.md)).

## The contracts

- **HTTP API** — `domain/contracts/api/behaviour-service.openapi.yaml` (OpenAPI). Source of
  truth for the HTTP surface. The implementation is checked against it with Schemathesis plus
  a spec-drift test (the served `/openapi.json` must not drift from the committed contract),
  and the mobile experience consumes it through a typed client generated from it
  (`task gen:client`).
- **Events** — `domain/contracts/api/behaviour-service.asyncapi.yaml` (AsyncAPI). Emitted
  events are validated against it in the integration test.
- **Data products** — named for the need they serve, not their shape:
  - `domain/contracts/data/colour-operational.contract.yaml` — **operational awareness** +
    long-term granular detail; raw JSONL.
  - `domain/contracts/data/colour-performance.contract.yaml` — **performance** over time +
    current status; curated Parquet.

  Each contract states its purpose, and both are verified against the real objects in
  SeaweedFS with `datacontract test`. The Streamlit app has a tab per product: **Operational
  Awareness** and **Performance**.
- **Event payload** — `domain/events/colour.generated.schema.json` (JSON Schema, CloudEvents).

Data contracts conform to the
[datacontract specification](https://github.com/datacontract/datacontract-specification).
Contract ids use the `urn:outcome-app-pattern:*` scheme.

## Linting and verification

- Lint all three contracts up front: `task ci` runs the contract lints as its first step
  (or lint them individually while authoring).
- Runtime conformance is covered in [testing](../testing/index.md): Schemathesis + spec-drift
  for the OpenAPI surface, the event contract test for AsyncAPI/CloudEvents, and
  `datacontract test` for the two data products.

## Evolution

All contracts here are `v1.0.0`. Decide the evolution rules before the first external
consumer exists — additive fields are minor versions; renames/removals are major versions
with a parallel-run window; the CloudEvent `type` (or a `dataschema` attribute) carries the
version signal for events; data contracts version the model and keep the old product until
consumers migrate. See [productionising](../productionising/index.md#contracts--evolution).
