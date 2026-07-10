# Documentation

The canonical topic index for this repo — for humans and agents alike. Entry files
(`README.md`, `AGENTS.md`) route here; each topic below owns its subject in
`docs/{topic}/index.md`, where the detailed documentation is kept.

| Topic | What it covers |
| --- | --- |
| [Architecture](architecture/index.md) | The pattern, the three zones, project layout, and the naming rules. |
| [Contracts](contracts/index.md) | The OpenAPI, AsyncAPI, and data contracts; contract-first and how they're verified. |
| [Development](development/index.md) | The contract-first order of work, conventions, local dev, the Taskfile, and product requirements. |
| [Testing](testing/index.md) | The conformance gates: Schemathesis, spec-drift, event contract, and `datacontract test`. |
| [Data products](data-products/index.md) | The operational and performance products, the system-of-record storage model, and the summariser. |
| [Deployment](deployment/index.md) | Running the whole stack locally via Docker Compose, and the single-node-demo boundaries. |
| [Productionising](productionising/index.md) | What the demo deliberately omits and what to add before running for real. |
| [Replication](replication/index.md) | The lift-out guide: replicating this pattern for your own domain, including a platform-swap case study. |
