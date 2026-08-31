# Roadmap

Last Reviewed: 2026-08-31

## Roadmap Summary

Ship a usable open-source dbt control plane via a modular monolith and Docker Compose, sequenced from steering/docs and a public marketing landing → vertical slice (manual LocalDocker run) → schedules, Batch, Elementary, then packaging polish. Delivery of code uses the local-first agent workflow on GitHub (`docs/superpowers/specs/2026-08-25-agent-delivery-workflow-design.md`).

Milestone order matches the MVP design (`docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md`) until this roadmap is revised.

## M1 — Steering and design lock

Linear project: [M1 — Steering and design lock](https://linear.app/medaiec/project/m1-steering-and-design-lock-bfcacfd44b3e)

- [DCP-10](https://linear.app/medaiec/issue/DCP-10) Durable steering on main (`PRODUCT`, `TECH`, `STRUCTURE`, `DESIGN`, `ROADMAP`, `AGENTS`, ADRs)
- [DCP-11](https://linear.app/medaiec/issue/DCP-11) Approved MVP design retained as implementation authority
- [DCP-12](https://linear.app/medaiec/issue/DCP-12) Implementation plan for the first vertical slice
- [DCP-29](https://linear.app/medaiec/issue/DCP-29) Public marketing landing at `www/` (static HTML; does not block M2)
- [DCP-30](https://linear.app/medaiec/issue/DCP-30) Repo CI + automerge setup (uv/pnpm toolchains, Actions checks `python`+`typescript`, rulesets; human arms feature→`dev` auto-merge; does not block M2)

## M2 — Domain and API foundation

Linear project: [M2 — Domain and API foundation](https://linear.app/medaiec/project/m2-domain-and-api-foundation-a60276847e39)

- [DCP-13](https://linear.app/medaiec/issue/DCP-13) Domain model and Postgres migrations for projects, environments, and jobs
- [DCP-14](https://linear.app/medaiec/issue/DCP-14) API CRUD for projects, environments, and jobs

## M3 — First vertical slice (LocalDocker)

Linear project: [M3 — First vertical slice (LocalDocker)](https://linear.app/medaiec/project/m3-first-vertical-slice-localdocker-f461faa69643)

- [DCP-16](https://linear.app/medaiec/issue/DCP-16) Docker Compose stack including the required local dbt runner image
- [DCP-15](https://linear.app/medaiec/issue/DCP-15) LocalDockerRunner plus one platform workflow for a manual run through artifacts and lineage
- [DCP-17](https://linear.app/medaiec/issue/DCP-17) Getting started UI plus project, job, and run detail for the slice
- [DCP-19](https://linear.app/medaiec/issue/DCP-19) Run logs, artifact index, and basic lineage visible in the UI

## M4 — Schedules

Linear project: [M4 — Schedules](https://linear.app/medaiec/project/m4-schedules-bfd7b46d7f25)

- [DCP-18](https://linear.app/medaiec/issue/DCP-18) Job schedules via DBOS with cron-driven runs

## M5 — AWS Batch runner

Linear project: [M5 — AWS Batch runner](https://linear.app/medaiec/project/m5-aws-batch-runner-91034041b9bb)

- [DCP-20](https://linear.app/medaiec/issue/DCP-20) AWSBatchRunner adapter behind the shared runner contract (Compose still boots without AWS)

## M6 — Elementary observability

Linear project: [M6 — Elementary observability](https://linear.app/medaiec/project/m6-elementary-observability-af3edc7179c4)

- [DCP-21](https://linear.app/medaiec/issue/DCP-21) Required Elementary step and split `observability_status` on runs

## M7 — Packaging and adopter docs

Linear project: [M7 — Packaging and adopter docs](https://linear.app/medaiec/project/m7-packaging-and-adopter-docs-c8ddd62ef696)

- [DCP-22](https://linear.app/medaiec/issue/DCP-22) Compose packaging polish and OSS adopter documentation (update landing CTA when runbooks exist)

## M8 — Later productization

Linear project: [M8 — Later productization](https://linear.app/medaiec/project/m8-later-productization-83914ea755cf)

- [DCP-24](https://linear.app/medaiec/issue/DCP-24) OIDC and RBAC
- [DCP-25](https://linear.app/medaiec/issue/DCP-25) Helm / Kubernetes packaging
- [DCP-23](https://linear.app/medaiec/issue/DCP-23) Temporal backend only if DBOS hits a proven limitation
- [DCP-27](https://linear.app/medaiec/issue/DCP-27) Multi-tenancy / multi-team productization
- [DCP-26](https://linear.app/medaiec/issue/DCP-26) Stronger design system and accessibility bar
- [DCP-28](https://linear.app/medaiec/issue/DCP-28) Delivery-platform automation beyond local agent-delivery skills

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

- ~~Choose Node/UI package manager before UI lockfile lands~~ **Decided:** pnpm (ADR-0008; lands with M1-D5 / [DCP-30](https://linear.app/medaiec/issue/DCP-30)). Python remains **uv** (ADR-0007)
- Confirm Elementary execution topology during implementation planning
- Revisit Temporal only with concrete DBOS limitation evidence

## Assumptions

- Milestone order from the MVP design remains authoritative until this roadmap is revised
- Agent-delivery on GitHub stays the engineering workflow for this repository
- M1-D4 (marketing landing) does not block M2 domain work
- M1-D5 (repo CI + automerge) does not block M2 domain work; prefer landing it before Agent Ready M2 PRs so merge gates exist

## Unknowns

- Public release naming/versioning scheme (v0.1 vs calendar versioning)
- Whether AWS Batch must be demoable in the same release train as Elementary or can trail by a patch
