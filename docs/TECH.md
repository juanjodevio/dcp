# Tech

Last Reviewed: 2026-08-31

## Technical Summary

Modular monolith: FastAPI API and DBOS worker in one process for v0.1, PostgreSQL for product state, S3-compatible object storage for artifacts, Next.js **operator** UI, dbt executed only via OCI runners. Target packaging is Docker Compose (local dbt runner image required). Application product source remains **planned** beyond a minimal `src/dcp` placeholder for CI. The public marketing landing is static HTML under `www/` and is not part of the Next.js app; Node under `www/` is for tests and CI only. The `/agent-delivery` verification entrypoint is documented in Commands.

Source design: `docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md`. CI and automerge: `docs/superpowers/specs/2026-08-31-repo-ci-automerge-setup-design.md`.

## Stack And Runtimes

- Language/runtime: Python 3.12 (API, orchestration, integrations); Node.js 22 / TypeScript (UI smoke + landing tests)
- Frameworks: FastAPI; SQLAlchemy 2 + Alembic; DBOS; Next.js (operator UI only — not scaffolded yet)
- Marketing landing: static HTML + CSS in `www/` (no Next.js build for the page)
- Database/storage: PostgreSQL (product + DBOS durable state); MinIO/S3-compatible artifact store
- Deployment target: Docker Compose first; Helm deferred
- Execution: required local dbt runner image; optional AWS Batch as an execution target when configured
- Telemetry: OpenTelemetry
- CI: GitHub Actions `.github/workflows/ci.yml`; required job names are exactly `python` and `typescript`

## Package Manager

- Python: **uv** (locked). Expect `pyproject.toml` + `uv.lock`; agents and CI must use `uv`, not pip/poetry directly for dependency resolution. See [ADR-0007](adr/0007-python-package-manager-uv.md).
- Node: **pnpm** (locked). Expect root `pnpm-workspace.yaml` and `pnpm-lock.yaml`; workspace packages `www` (`@dcp/www`) and `control-plane/ui` (`@dcp/ui`). CI installs with `pnpm install --frozen-lockfile`. See [ADR-0008](adr/0008-node-package-manager-pnpm.md).

## Commands

`/agent-delivery` verification entrypoint (also listed in `AGENTS.md`):

```bash
pnpm --filter @dcp/www test
```

Landing copy/CTA/asset contract (Vitest under `www/tests/`). **Verified** locally. Record pass/fail against the feature SHA. Do not claim success if the command is missing, errors, or exits non-zero.

Full local CI parity (Actions jobs `python` and `typescript`):

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
pnpm install --frozen-lockfile
pnpm lint
pnpm format:check
pnpm typecheck
pnpm test
```

CI uses `uv sync --frozen` instead of `uv sync`. Python and TypeScript command sets were verified locally after toolchain bootstrap.

Marketing landing preview (not the verification entrypoint):

```bash
python3 -m http.server -d www 4173
```

Other commands remain planned until application scaffolds land:

- Local stack: `docker compose up` (planned)
- Validate: compose health + API health endpoint (planned)

AI PR review is deferred (CodeRabbit radar). Do not put review vendor secrets in Actions.

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

Present tooling (CI / verification):

- Ruff, mypy, pytest via uv
- ESLint, Prettier, TypeScript, Vitest via pnpm

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
- Required CI check names are a contract: renaming `python` or `typescript` requires a simultaneous ruleset update

## Assumptions

- DBOS remains sufficient for coarse platform workflows in v0.1 (accepted product decision; Temporal only if proven limitation)
- Compose always ships the local dbt runner image even when Batch is configured
- Split run fields: `dbt_status` and `observability_status`

## Unknowns

- Exact DBOS APIs for durable wait/poll and schedule registration (resolve against current DBOS docs at implementation)
- Secret-ref mechanism for warehouse credentials in Compose (env file vs mounted secret)
- Whether Elementary co-runs in the dbt container or as a second invocation
