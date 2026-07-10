# Testing

The drift gates are the pattern's teeth: they make it impossible for the implementation to
silently diverge from the contracts. Keep them in CI for every domain you stand up.

## The gates

| Gate | What it proves | Command |
| --- | --- | --- |
| **Unit** | Behaviour-service logic, hermetic (no stack). | `task test:unit` |
| **Schemathesis conformance** | The running API conforms to the committed OpenAPI contract (property-based, generated cases). | `task test:integration` |
| **Spec-drift** | The served `/openapi.json` has not drifted from the committed OpenAPI file. | `task test:integration` |
| **Event contract** | Emitted `colour.generated` events validate against the AsyncAPI contract + CloudEvents schema, round-tripped through the outbox. | `task test:integration` |
| **`datacontract test`** | Both data products (`colour-operational`, `colour-performance`) match their data contracts against the **real objects** in SeaweedFS. | `task test:contract:data` |

## How they run

- `task ci` runs the contract lints, the unit tests, the runtime-conformance suite, and the
  data-product tests — the one command agents, developers, and CI all invoke.
- The integration suite needs the API running; the data-product test needs the full stack up
  (`task up`) because it reads the actual stored objects over S3.

## Why it matters

Because the contracts are authored first and the tests check the implementation *against*
them, a change that breaks the HTTP surface, the event shape, or a data-product schema fails
CI rather than reaching a consumer. When you replicate the pattern, these gates travel with
it — see [replication](../replication/index.md) and, for the production stance on keeping them
on, [productionising](../productionising/index.md#contracts--evolution).
