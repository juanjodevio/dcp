# Roadmap

Last Reviewed: 2026-08-25

## Roadmap Summary

Ship a usable open-source dbt control plane via a modular monolith and Docker Compose, sequenced from steering/docs → vertical slice (manual LocalDocker run) → schedules, Batch, Elementary, then packaging polish. Delivery of code uses the local-first agent workflow on GitHub (`docs/superpowers/specs/2026-08-25-agent-delivery-workflow-design.md`).

## Now

- Establish durable steering (`PRODUCT`, `TECH`, `STRUCTURE`, `DESIGN`, `ROADMAP`, `AGENTS`, ADRs)
- Approve MVP design and write implementation plan
- Domain + API CRUD (projects, environments, jobs) + Postgres migrations
- First vertical slice: Compose (with required local dbt runner image) → Getting started → manual LocalDocker run → logs, artifacts, basic lineage

## Next

- UI depth for project/job/run flows beyond the slice
- Schedules via DBOS
- AWSBatchRunner adapter (Compose still boots without AWS)
- Elementary required step + `observability_status`
- Compose packaging polish and OSS adopter docs

## Later

- OIDC + RBAC
- Helm / Kubernetes packaging
- Temporal backend only if DBOS hits a proven limitation
- Multi-tenancy / multi-team productization
- Stronger design system and accessibility bar
- Delivery-platform automation beyond local agent-delivery skills

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
