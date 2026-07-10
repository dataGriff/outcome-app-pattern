# Data products

Two products, named for the need they serve rather than their shape. The analytical side
reads these products — never the domain's operational store.

| Product | Purpose | Shape |
| --- | --- | --- |
| `colour-operational` | Operational awareness — react to what's happening now, in granular detail; also the long-term durable record. | Append-only raw **JSONL**. |
| `colour-performance` | Performance over time + where things stand right now. | Curated daily aggregate, columnar **Parquet**. |

Both are verified against the real objects in SeaweedFS with `datacontract test` (see
[testing](../testing/index.md)), and each gets its own tab in the Streamlit app.

## The flow

`platform/streaming/` (bento) streams `colour.generated` events from NATS into object storage
under `colour-operational/`. The **summariser** (`platform/analytics/summariser/`) rolls the
raw stream up into the curated daily aggregate under `colour-performance/`.

```
NATS → bento → colour-operational/ (raw JSONL, system of record)
                     │
                     ▼  summariser
              colour-performance/ (curated daily Parquet)
```

## Treat the raw product as the system of record

The raw operational product is the **durable record** — keep it immutably. The naive
summariser recomputes from the whole raw history every run, which does not scale. The
platform-agnostic upgrade (surfaced by the Cloudflare dry-run, see
[replication](../replication/index.md)):

- **Date-partition** the raw product (`dt=YYYY-MM-DD/`) and keep it immutable.
- Make the summariser **incremental**: recompute only an *open window* of recent days.
- **Seal** each closed day once — write its curated partition, compact its raw fragments — and
  advance a **watermark** so sealed days are never re-read.

Cold-tiering the sealed archive to cheaper storage (e.g. S3 Infrequent Access via a lifecycle
rule) is a separate, paid production lever, distinct from the logical tiering above.
