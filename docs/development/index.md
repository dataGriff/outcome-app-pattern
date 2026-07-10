# Development

How this repo is built and worked on. This consolidates what used to live in
`.github/instructions/` — it is the single source of truth for the order of work,
conventions, and local development.

## Product requirements

The demo's user stories keep the pattern honest with a trivial feature:

- **As an application user**, I want to click a button and see a random red / amber / green
  colour, so that I can discover new colours.
- **As a decision maker**, I want to see a count of how many times the button has been
  clicked (and which colours came up), so that I can track interactions.

Everything except the word "colour" is the pattern; the feature is deliberately trivial.

## Order of work

Contract-first, in this order — the same order used to build the repo:

1. **Contracts** — author the OpenAPI spec, the AsyncAPI spec, and one data contract per data
   product *before* implementation. Validate and lint each (`task ci` runs the lints). See
   [contracts](../contracts/index.md).
2. **Infrastructure** — compose services for the operational store, event broker, and object
   storage. Role-name them (see [architecture](../architecture/index.md#naming-rules)).
3. **Behaviour** — the API + operational schema + transactional outbox + relay, test-first.
   Verify against the contracts: Schemathesis conformance, the spec-drift test, and the event
   contract test.
4. **Data products** — the streaming pipeline for the raw product, the batch summariser for
   the curated product, test-first. Verify with `datacontract test` against real objects.
   Treat the raw product as the durable system of record — see
   [data products](../data-products/index.md).
5. **Experiences** — one channel at a time, each consuming the API (typed client generated
   from the committed OpenAPI spec: `task gen:client`). Then the reporting experience over the
   data products.
6. **CI** — everything above runs through one `task ci`, so agents, developers, and CI execute
   the identical commands.

The application is "done" for a phase when it works end to end through the experience UI and
the reporting UI reflects changes.

## Conventions

- **Conventional commits** (`feat:`, `fix:`, `docs:`, `chore:`).
- **Contract-first**, **test-driven** development.
- **Event-driven** patterns; CloudEvents over AsyncAPI.
- Application behaviour is **decoupled from the data product**.
- **Local-first and isolation** — the whole stack runs from `docker-compose.yml`.
- **Role-name infrastructure, purpose-name data products** (see
  [architecture](../architecture/index.md#naming-rules)).

## The Taskfile — one set of commands

Any repetitive task that CI also needs lives in `Taskfile.yml`, so agents, developers, and CI
run the *same* thing. Don't duplicate a lint/test/build/run command across contexts — add it
to the Taskfile and reference it everywhere.

```bash
task up                 # build + start the whole stack
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

## Local development

Run `task up`, then exercise the stack — see [deployment](../deployment/index.md) for the
full service/URL table. The quick loop: click **Generate** in the web or mobile UI, or
`curl -X POST localhost:8000/colours`; watch the live feed update in every experience, then
see the event land under `colour-operational/`, the summariser roll it into
`colour-performance/`, and the Streamlit counts move.
