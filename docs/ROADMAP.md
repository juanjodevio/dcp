# Roadmap

Last Reviewed: 2026-08-25

## Roadmap Summary

Ship a usable open-source dbt control plane via a modular monolith and Docker Compose, sequenced from steering/docs → vertical slice (manual LocalDocker run) → schedules, Batch, Elementary, then packaging polish. Delivery of code uses the local-first agent workflow on GitHub (`docs/superpowers/specs/2026-08-25-agent-delivery-workflow-design.md`).

Milestone order matches the MVP design (`docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md`) until this roadmap is revised.

## M1 — Steering and design lock

- [M1-D1] Durable steering on main (`PRODUCT`, `TECH`, `STRUCTURE`, `DESIGN`, `ROADMAP`, `AGENTS`, ADRs)
- [M1-D2] Approved MVP design retained as implementation authority
- [M1-D3] Implementation plan for the first vertical slice

## M2 — Domain and API foundation

- [M2-D1] Domain model and Postgres migrations for projects, environments, and jobs
- [M2-D2] API CRUD for projects, environments, and jobs

## M3 — First vertical slice (LocalDocker)

- [M3-D1] Docker Compose stack including the required local dbt runner image
- [M3-D2] LocalDockerRunner plus one platform workflow for a manual run through artifacts and lineage
- [M3-D3] Getting started UI plus project, job, and run detail for the slice
- [M3-D4] Run logs, artifact index, and basic lineage visible in the UI

## M4 — Schedules

- [M4-D1] Job schedules via DBOS with cron-driven runs

## M5 — AWS Batch runner

- [M5-D1] AWSBatchRunner adapter behind the shared runner contract (Compose still boots without AWS)

## M6 — Elementary observability

- [M6-D1] Required Elementary step and split `observability_status` on runs

## M7 — Packaging and adopter docs

- [M7-D1] Compose packaging polish and OSS adopter documentation

## M8 — Later productization

- [M8-D1] OIDC and RBAC
- [M8-D2] Helm / Kubernetes packaging
- [M8-D3] Temporal backend only if DBOS hits a proven limitation
- [M8-D4] Multi-tenancy / multi-team productization
- [M8-D5] Stronger design system and accessibility bar
- [M8-D6] Delivery-platform automation beyond local agent-delivery skills

## Non-Goals

- Reimplementing dbt internals or a custom model DAG executor
- Kafka/Redis as early infrastructure
- Auth in the first usable release
- Cursor Origin as the primary forge for this repo (GitHub selected)
- Building a separate delivery-platform service before validating manual agent-delivery

## Risks And Dependencies

- DBOS durable wait/schedule APIs may constrain long-running runner waits — mitigate with Runner handle + poll/timer pattern; Temporal only if blocked
- Elementary invocation shape (co-locate vs second step) may affect runner images
- Dual runners in v0.1 increase surface area — keep one contract; ship LocalDocker path first in the vertical slice
- No auth increases exposure risk if operators bind publicly — document private-network assumption

## Decision Points

- Choose Node/UI package manager before UI lockfile lands (Python is **uv**; see ADR-0007)
- Confirm Elementary execution topology during implementation planning
- Revisit Temporal only with concrete DBOS limitation evidence

## Assumptions

- Milestone order from the MVP design remains authoritative until this roadmap is revised
- Agent-delivery on GitHub stays the engineering workflow for this repository

## Unknowns

- Public release naming/versioning scheme (v0.1 vs calendar versioning)
- Whether AWS Batch must be demoable in the same release train as Elementary or can trail by a patch
