# Productionising checklist

The demo keeps the pattern legible by deliberately omitting production machinery. Each
omission below is a decision to revisit — not an oversight — before running this pattern
for real.

## Delivery semantics

- **Idempotent consumers.** The outbox relay is at-least-once: a crash between the NATS
  publish and the `published_at` mark redelivers the event. Consumers must dedupe — the
  CloudEvent `id` is the natural key. The demo's consumers tolerate duplicates trivially
  (append-only raw product, full-recompute summariser); a real consumer needs an explicit
  seen-ids store or idempotent upsert.
- **Relay high availability.** One relay replica, by design (`FOR UPDATE SKIP LOCKED`
  makes multiple replicas *safe*, but ordering across replicas is not guaranteed). For HA,
  run replicas and accept per-subject reordering, or add leader election.
- **Dead-lettering & retry policy.** A poison outbox row (broker rejects it forever) would
  block nothing but retry forever. Add a retry count + DLQ table/subject after N attempts.
  Same on the consuming side: the streaming pipeline should route unparseable events to a
  dead-letter output instead of dropping or crash-looping.
- **Outbox retention.** Implemented in the demo (the relay prunes published rows older
  than `OUTBOX_RETENTION_SECONDS`); tune the retention to your audit needs — published
  rows are a delivery log, not history.

## Contracts & evolution

- **Schema evolution strategy.** All contracts here are v1.0.0 and only additive change is
  demonstrated-by-absence. Decide the rules before the first consumer exists: additive
  fields are minor versions; renames/removals are major versions with a parallel-run
  window; the CloudEvent `type` (or a `dataschema` attribute) carries the version signal
  for events; data contracts version the model and keep the old product until consumers
  migrate.
- **Drift gates stay on.** The Schemathesis conformance run, the spec-drift test, the
  event contract test, and `datacontract test` are the pattern's teeth — keep them in CI
  for every domain you stand up.

## Observability

- **Structured logs exist; metrics and traces don't.** Add request tracing (correlation
  id propagated API → outbox payload → relay → broker → pipeline), publish-lag and
  outbox-depth metrics on the relay, and data-product freshness metrics that alert against
  the service levels the data contracts already declare.

## Security & operations

- **Secrets.** `platform/storage/s3.json` and the compose `demokey`/`demosecret` values
  are committed *only* because this is a disposable local demo. In production: a secrets
  manager, per-service credentials, and TLS on the broker, store, and API.
- **AuthN/AuthZ.** The API is open and CORS is `*`. Add authentication at the edge and
  scope CORS to real origins.
- **Backups & DR.** The operational store and object storage are single-node volumes.
  Production needs Postgres backups/replication and durable object storage.
- **Scale-out.** The SSE fan-out is in-process (one API replica). Multiple API replicas
  need a shared subscription (each replica already subscribes to the broker, so this
  mostly works — verify sticky/timeout behaviour with your load balancer).
