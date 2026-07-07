-- Operational store for the behaviour domain. Mounted into postgres via
-- docker-entrypoint-initdb.d so the schema exists on first boot.

CREATE TABLE IF NOT EXISTS colours (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    colour     text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Transactional outbox: written in the same transaction as the colour above,
-- drained to NATS by the relay. This is what removes the dual-write.
CREATE TABLE IF NOT EXISTS outbox (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    subject      text NOT NULL,
    payload      jsonb NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now(),
    published_at timestamptz
);

CREATE INDEX IF NOT EXISTS outbox_unpublished_idx
    ON outbox (created_at)
    WHERE published_at IS NULL;
