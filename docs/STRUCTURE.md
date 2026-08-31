# Structure

Last Reviewed: 2026-08-31

## Repository Overview

This repository holds the **dcp** product (modular monolith), a static public landing under `www/`, plus durable steering docs and agent-delivery skills. Application packages under `control-plane/` are **planned** except a minimal TypeScript smoke package at `control-plane/ui/`. Python currently has a placeholder package at `src/dcp/` so CI has a typecheck and pytest target.

## Directory Map

### Present

- `docs/PRODUCT.md`, `TECH.md`, `STRUCTURE.md`, `DESIGN.md`, `ROADMAP.md`: durable steering
- `docs/adr/`: architecture decision records
- `docs/superpowers/specs/`, `docs/superpowers/plans/`: brainstorming specs and implementation plans
- `docs/session-handoff.md`: prior session notes (historical; prefer steering + MVP design for truth)
- `.cursor/skills/` / `.cursor/agents/`: agent-delivery, planner, frontend-developer, cto
- `.github/workflows/ci.yml`: GitHub Actions jobs `python` and `typescript` (always run; no path filters)
- `pyproject.toml`, `uv.lock`, `src/dcp/`: Python package placeholder + Ruff/mypy/pytest
- `pnpm-workspace.yaml`, `pnpm-lock.yaml`, root `package.json`: pnpm workspace (`www`, `control-plane/ui`)
- `www/`: static marketing landing (HTML/CSS); Vitest landing contract in `www/tests/`
- `control-plane/ui/`: TypeScript smoke package (`@dcp/ui`)
- `tests/test_smoke.py`: Python smoke test

### Planned application layout

```text
control-plane/
  core/            # domain; no orchestrator/cloud SDK imports
    projects/
    environments/
    jobs/
    runs/
    workflows/
  api/             # FastAPI
  orchestration/   # WorkflowEngine + DBOS backend
  runners/         # Runner protocol, docker, aws_batch
  integrations/    # dbt, elementary
  storage/         # postgres, artifacts
  ui/              # Next.js operator UI (smoke package present)
www/                 # static marketing landing (not Compose UI)
```

- `docker-compose.yml` (planned): API+DBOS, Postgres, MinIO, UI, **required local dbt runner image**

## Ownership Boundaries

- `core/`: product entities and rules; no FastAPI/DBOS/AWS/Elementary imports
- `api/`: HTTP adapters only
- `orchestration/`: workflow engine adapters; domain starts workflows via ports
- `runners/`: execution adapters only
- `integrations/`: dbt artifact parsing and Elementary client boundaries
- `storage/`: persistence and object storage adapters
- `ui/`: operator presentation; talks to API
- `www/`: public marketing landing; static HTML/CSS; Node tooling here is tests/CI only; must not import control-plane product code
- `src/dcp/`: Python package placeholder until control-plane Python packages land
- `docs/`: durable truth; implementation agents should not silently rewrite product intent

## Placement Rules

- New domain behavior: `control-plane/core/`
- New HTTP routes: `control-plane/api/`
- New runner: `control-plane/runners/` implementing the shared protocol
- New marketing landing work: `www/` (see `docs/DESIGN.md` landing pack)
- Landing contract tests: `www/tests/` (not `tests/www`)
- Durable product/tech/design/roadmap changes: corresponding `docs/*.md` and ADRs when warranted
- Agent skills for delivery: `.cursor/skills/` (and agents under `.cursor/agents/`)
- Specs/plans from superpowers workflow: `docs/superpowers/`

## Tests And Fixtures

- Landing copy/CTA/asset contract: Vitest at `www/tests/landing-copy.test.ts`. Python `tests/www` landing tests are removed.
- Python smoke: `tests/test_smoke.py`.
- UI smoke: `control-plane/ui/src/smoke.test.ts`.
- Domain tests: planned under `tests/` when `control-plane/core/` exists. Prefer fixtures with sample dbt `manifest.json` / `run_results.json` under a dedicated fixtures directory—not production object storage.

## Generated Files And Artifacts

- Alembic versions: generated migrations committed after review
- Run artifacts in MinIO/S3: not source; do not commit
- Local agent-delivery run state: ignored directories (see agent-delivery design)—do not commit
- `node_modules/`, `.venv/`: generated; not source

## Assumptions

- Single repo for product + steering + delivery skills (no separate delivery-platform repo for now)
- Planned `control-plane/` layout matches the accepted MVP design
- pnpm workspace packages stay `www` and `control-plane/ui` until a later layout ADR

## Unknowns

- Exact layout of future `control-plane/` Python packages relative to the current `src/dcp/` placeholder
- Whether worktree-only skills under `.worktrees/` are promoted before first application code
