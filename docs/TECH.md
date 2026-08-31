# Tech

Last Reviewed: 2026-08-28

## Technical Summary

Modular monolith: FastAPI API and DBOS worker in one process for v0.1, PostgreSQL for product state, S3-compatible object storage for artifacts, Next.js **operator** UI, dbt executed only via OCI runners. Target packaging is Docker Compose (local dbt runner image required). Application source tree is **planned**; app install/lint/compose commands below are unverified until scaffolds exist. The public marketing landing is static HTML under `www/` and is not part of the Next.js app. The `/agent-delivery` verification entrypoint is documented in Commands.

Source design: `docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md`.

## Stack And Runtimes

- Language/runtime: Python (API, orchestration, integrations); Node.js/TypeScript (UI)
- Frameworks: FastAPI; SQLAlchemy 2 + Alembic; DBOS; Next.js (operator UI only)
- Marketing landing: static HTML + CSS in `www/` (no Node toolchain)
- Database/storage: PostgreSQL (product + DBOS durable state); MinIO/S3-compatible artifact store
- Deployment target: Docker Compose first; Helm deferred
- Execution: required local dbt runner image; optional AWS Batch as an execution target when configured
- Telemetry: OpenTelemetry

## Package Manager

- Python: **uv** (locked). Expect `pyproject.toml` + `uv.lock`; agents and CI must use `uv`, not pip/poetry directly for dependency resolution.
- UI: **pnpm** preferred for Next.js — **Unknown**; not chosen yet (no `package.json` in tree)

Evidence: Python choice is human-confirmed (2026-08-25). Lockfiles not in tree yet. Do not invent install commands as verified until scaffolds exist. See [ADR-0007](adr/0007-python-package-manager-uv.md).

## Commands

`/agent-delivery` verification entrypoint (also listed in `AGENTS.md`):

```bash
python3 -m unittest tests/www/test_landing_copy.py
```

This is the current repo entrypoint (landing copy contract; stdlib `unittest`, no `uv` yet). Record pass/fail against the feature SHA. Do not claim success if the command is missing, errors, or exits non-zero. It is expected to fail until DCP-29 adds `tests/www/test_landing_copy.py` and `www/`.

Marketing landing preview (not the verification entrypoint):

```bash
python3 -m http.server -d www 4173
```

Other commands remain planned until application scaffolds land:

- Install (Python): `uv sync` (planned; unverified)
- Lint / typecheck / test / build: TBD via `uv run ...` and stable scripts for agent-delivery and CI
- Local stack: `docker compose up` (planned)
- Validate: compose health + API health endpoint (planned)

When app commands are added, update this section with exact invocations and mark them verified after first successful run.

## Dependencies

Planned core dependencies (not installed yet):

- FastAPI / Uvicorn: HTTP API
- SQLAlchemy 2 + Alembic: ORM and migrations
- DBOS: durable workflows and scheduling
- Next.js: operator UI
- Static landing: `www/index.html` (no framework)
- OpenTelemetry SDK: traces/metrics
- AWS SDK (Batch adapter only): behind runner adapter; not a core domain import
- dbt: runs inside the runner image, not embedded in the API process

## Integrations And Services

- **dbt Core**: invoke via runner; consume `manifest.json`, `run_results.json`, logs
- **Elementary**: required observability step; reports stored as artifacts and linked to runs
- **Git**: checkout at SHA/ref for runs
- **Object storage**: ArtifactStore protocol (Filesystem/MinIO/S3)
- **AWS Batch**: optional runner implementation
- **OIDC**: deferred past v0.1

## Constraints And Conventions

- Domain/core code must not import DBOS, Temporal, AWS SDKs, or Elementary clients
- Orchestration behind `WorkflowEngine`; execution behind `Runner`; blobs behind `ArtifactStore`
- Control-plane **run ID** is the system-wide correlation ID
- Do not execute dbt’s model DAG from the control plane
- Prefer adapters over baking cloud assumptions into domain models
- Auth middleware is out of scope for v0.1; document private-network / localhost assumption

## Assumptions

- DBOS remains sufficient for coarse platform workflows in v0.1 (accepted product decision; Temporal only if proven limitation)
- Compose always ships the local dbt runner image even when Batch is configured
- Split run fields: `dbt_status` and `observability_status`

## Unknowns

- Node/UI package manager (pnpm candidate, not locked)
- Exact DBOS APIs for durable wait/poll and schedule registration (resolve against current DBOS docs at implementation)
- Secret-ref mechanism for warehouse credentials in Compose (env file vs mounted secret)
- Whether Elementary co-runs in the dbt container or as a second invocation
