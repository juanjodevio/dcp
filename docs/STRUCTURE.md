# Structure

Last Reviewed: 2026-08-28

## Repository Overview

This repository will hold the **dcp** product (modular monolith), a static public landing under `www/`, plus durable steering docs and agent-delivery skills. Application packages under `control-plane/` are **planned** and not present yet. Existing tree is mostly docs and planning artifacts.

## Directory Map

### Present

- `docs/PRODUCT.md`, `TECH.md`, `STRUCTURE.md`, `DESIGN.md`, `ROADMAP.md`: durable steering
- `docs/adr/`: architecture decision records
- `docs/superpowers/specs/`, `docs/superpowers/plans/`: brainstorming specs and implementation plans
- `docs/session-handoff.md`: prior session notes (historical; prefer steering + MVP design for truth)
- `.cursor/skills/` / `.cursor/agents/`: may live on feature branches/worktrees for agent-delivery and plan-roadmap (see worktrees); promote to main as those skills land
- `www/`: planned static marketing landing (not the operator UI)

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
  ui/              # Next.js operator UI
www/                 # static marketing landing (not Compose UI)
```

- `docker-compose.yml` (planned): API+DBOS, Postgres, MinIO, UI, **required local dbt runner image**
- CI under `.github/` (planned) for deterministic checks on GitHub

## Ownership Boundaries

- `core/`: product entities and rules; no FastAPI/DBOS/AWS/Elementary imports
- `api/`: HTTP adapters only
- `orchestration/`: workflow engine adapters; domain starts workflows via ports
- `runners/`: execution adapters only
- `integrations/`: dbt artifact parsing and Elementary client boundaries
- `storage/`: persistence and object storage adapters
- `ui/`: operator presentation; talks to API
- `www/`: public marketing landing; static files only; must not import control-plane code
- `docs/`: durable truth; implementation agents should not silently rewrite product intent

## Placement Rules

- New domain behavior: `control-plane/core/`
- New HTTP routes: `control-plane/api/`
- New runner: `control-plane/runners/` implementing the shared protocol
- New marketing landing work: `www/` (see `docs/DESIGN.md` landing pack)
- Durable product/tech/design/roadmap changes: corresponding `docs/*.md` and ADRs when warranted
- Agent skills for delivery: `.cursor/skills/` (and agents under `.cursor/agents/`)
- Specs/plans from superpowers workflow: `docs/superpowers/`

## Tests And Fixtures

Planned: colocate or mirror under `tests/` (exact layout **Unknown** until the app scaffold). Landing copy tests live at `tests/www/test_landing_copy.py` once M1-D4 is implemented. Prefer fixtures with sample dbt `manifest.json` / `run_results.json` under a dedicated fixtures directory—not production object storage.

## Generated Files And Artifacts

- Alembic versions: generated migrations committed after review
- Run artifacts in MinIO/S3: not source; do not commit
- Local agent-delivery run state: ignored directories (see agent-delivery design)—do not commit

## Assumptions

- Single repo for product + steering + delivery skills (no separate delivery-platform repo for now)
- Planned `control-plane/` layout matches the accepted MVP design

## Unknowns

- Exact Python package layout (`src/` vs flat) under uv/`pyproject.toml`, and operator UI package path if monorepo tools require `apps/web`
- Whether worktree-only skills under `.worktrees/` are promoted before first application code
