# AGENTS.md

The canonical working agreement for anyone — human or agent — changing this repo.
Keep it thin: durable rules live here, everything else routes through
[`docs/index.md`](docs/index.md).

## What this repo is

A reference demonstrator for a **source-aligned, API-first, multichannel domain**. One
place (`domain/`) owns the behaviour API, the operational store, the events, and all
contracts; multiple `experiences/` (web, mobile, agent) consume that *same* contract; the
`platform/` runs streaming, storage, and analytics over the data products. The trivial
"generate a colour" example keeps the **pattern** in focus, not the feature. See
[`docs/architecture/`](docs/architecture/index.md).

## Working agreement

- **Contract-first.** Author and lint the OpenAPI, AsyncAPI, and data contracts *before*
  the implementation they describe. The build order is contracts → infrastructure →
  behaviour → data products → experiences → CI. Full detail:
  [`docs/development/`](docs/development/index.md).
- **Test-driven.** Write the test with the contract, then the code. The drift gates
  (Schemathesis, spec-drift, event contract, `datacontract test`) are the pattern's teeth —
  keep them green. See [`docs/testing/`](docs/testing/index.md).
- **One `task ci`.** Agents, developers, and CI all run the *same* Taskfile targets — never
  duplicate a lint/test/build command across contexts; add it to the Taskfile and reference
  it everywhere.
- **Conventional commits** (`feat:`, `fix:`, `docs:`, `chore:`).
- **Role-name infrastructure, purpose-name data products** — see the naming rules in
  [`docs/architecture/`](docs/architecture/index.md).

## Documentation hub

All topics live in **[`docs/index.md`](docs/index.md)** — route through it. Entry files
(this one, `README.md`) stay thin and point there; the fanned-out documentation lives in
`docs/{topic}/index.md`.

## Keeping docs correct

When something changes, update the matching topic so the docs stay true:

| You changed… | Update… |
| --- | --- |
| A contract (OpenAPI / AsyncAPI / data) | [`docs/contracts/`](docs/contracts/index.md) |
| The build order, conventions, or a Taskfile target | [`docs/development/`](docs/development/index.md) |
| A test or conformance gate | [`docs/testing/`](docs/testing/index.md) |
| The data products / storage layout / summariser | [`docs/data-products/`](docs/data-products/index.md) |
| Zones, roles, or the pattern shape | [`docs/architecture/`](docs/architecture/index.md) |
| How the stack runs locally | [`docs/deployment/`](docs/deployment/index.md) |
| A production-readiness gap | [`docs/productionising/`](docs/productionising/index.md) |
| The replication / lift-out guidance | [`docs/replication/`](docs/replication/index.md) |
