# platform/storage — object storage (SeaweedFS)

The data product lands in an S3-compatible object store. We use
[SeaweedFS](https://github.com/seaweedfs/seaweedfs) (Apache-2.0) rather than a
proprietary store so the whole demo runs locally with no external dependency.

`s3.json` grants a single fixed demo identity (`demokey` / `demosecret`). Both
the streaming pipeline (`platform/streaming`) and the analytics consumers
(`platform/analytics`) authenticate with these same static credentials, so there
is no runtime secret to surface.

> ⚠️ These credentials are committed **only** because this is a throwaway local
> demo. Never commit real object-storage keys.

Unlike MinIO's root user, SeaweedFS has no admin login; access is entirely via the
identities in `s3.json`. Buckets do not auto-create on write, so
`docker-compose.yml` runs a one-shot `seaweedfs-init` container that creates
`mybucket` via `weed shell` before the pipeline starts writing.

Ports (from `docker-compose.yml`): `8333` S3 API · `8888` filer UI · `9333` master UI.
