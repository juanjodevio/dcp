# AGENTS.md

## Project Summary

**dcp** is an open-source, self-hostable dbt Core control plane (projects, environments, jobs, schedules, runs, artifacts, lineage, Elementary). v0.1 is a modular monolith on Docker Compose with DBOS workflows and LocalDocker + AWS Batch runners. Application code is not scaffolded yet—steering docs and the MVP design are the source of truth. The public marketing landing is static files under `www/` (not the operator UI).

## First Reads

- `docs/PRODUCT.md` — users, scope, workflows, success criteria
- `docs/STRUCTURE.md` — planned layout and boundaries
- `docs/TECH.md` — stack, constraints, commands
- `docs/DESIGN.md` — operator screens, landing vs app skill packs (same `frontend-developer` agent)
- `docs/ROADMAP.md` — now/next/later and non-goals
- `docs/adr/` — durable decisions ([index](docs/adr/index.md))
- `docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md` — approved MVP design detail
- `docs/superpowers/specs/2026-08-25-agent-delivery-workflow-design.md` — agent delivery on GitHub
- `docs/superpowers/specs/2026-08-28-marketing-landing-design.md` — public landing (M1-D4)

## Commands

Verification entrypoint: `python3 -m unittest tests/www/test_landing_copy.py` (owning list: `docs/TECH.md`). `/agent-delivery` must record evidence for this command against the feature SHA; do not invent success. Python package manager is **uv** ([ADR-0007](docs/adr/0007-python-package-manager-uv.md)). Planned app commands (`uv sync`, `docker compose up`) remain in `docs/TECH.md` until scaffolds land.

## Agent Workflow

- Read steering docs and relevant ADRs before changing durable behavior.
- Keep domain/core free of DBOS, Temporal, AWS SDK, and Elementary imports.
- Do not reimplement dbt’s model DAG; invoke dbt via runners and consume artifacts.
- Feature work targets `dev`; milestone releases use `dev` → `main`. Delivery uses `/plan-roadmap` and thin `/agent-delivery` wrapping Superpowers (SDD, review, finish), with project `frontend-developer` for operator UI **and** marketing landing tickets (see agent-delivery design). Landing vs operator still use different skill packs in `docs/DESIGN.md`.
- Update the owning steering doc (or add a superseding ADR) when durable truth changes—do not only patch `AGENTS.md`.

## Delivery Workflow

Linear team: DCP

Required issue states: `Needs Planning`, `Agent Ready`.

When repair cycles are exhausted, `/agent-delivery` writes a Linear status note and applies the issue label `blocked-human` (Linear has no dedicated Blocked workflow state). Do not invent a Blocked status.

## Safety And Approval Boundaries

- Ask before changing product intent, roadmap priority, public contracts, security/auth posture, or accepted ADR direction.
- Do not rewrite accepted ADRs; supersede with a new ADR.
- Do not treat prompts as security boundaries.
- Implementation agents should not silently edit steering docs to fit a ticket; CTO/human path owns steering drift.

## Durable Truth Maintenance

`AGENTS.md` points to truth; it must not duplicate PRODUCT/TECH/ROADMAP/ADR content.
