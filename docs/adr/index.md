# docs/adr index

Manual ADR maintenance (`adr-tools` was not available when this directory was initialized).

| ADR | Status | Decision |
| --- | --- | --- |
| [ADR-0001](./0001-record-architecture-decisions.md) | Accepted | Use Markdown ADRs under `docs/adr/` |
| [ADR-0002](./0002-modular-monolith.md) | Accepted | Ship v0.1 as a modular monolith |
| [ADR-0003](./0003-dbos-workflow-engine.md) | Accepted | Use DBOS behind WorkflowEngine for v0.1 |
| [ADR-0004](./0004-runner-and-artifact-adapters.md) | Accepted | Runner + ArtifactStore protocols; LocalDocker required; Batch optional target |
| [ADR-0005](./0005-normalize-core-lineage-metadata.md) | Accepted | Normalize core lineage in Postgres; raw artifacts in object storage |
| [ADR-0006](./0006-defer-auth-require-elementary.md) | Accepted | No auth in v0.1; Elementary required |
| [ADR-0007](./0007-python-package-manager-uv.md) | Accepted | Python package manager is uv |
| [ADR-0008](./0008-node-package-manager-pnpm.md) | Accepted | Node package manager is pnpm |
