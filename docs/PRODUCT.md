# Product

Last Reviewed: 2026-08-25

## Product Summary

**dcp** is an open-source, self-hostable control plane for **dbt Core**, with **Elementary** as a required observability integration. It aims to provide an open-source alternative to commercial “dbt Cloud–like” operations: projects, environments, jobs, schedules, runs, artifacts, lineage, and coarse workflow orchestration—without locking the product core to a single cloud or orchestrator vendor.

Canonical MVP design: `docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md`.

## Target Users

- Open-source adopter / data engineer: discovers the project, self-hosts via Docker Compose, runs dbt jobs, and inspects runs, artifacts, lineage, and Elementary reports.
- Contributor / evaluator: runs the stack locally to try the product (v0.1 is single-user; no auth).

## Problem And Purpose

Teams that want Cloud-like job/run UX around dbt Core often face either commercial lock-in or cobbling together CI, schedulers, and ad-hoc scripts. dcp centralizes project/environment/job/run state, launches dbt through replaceable runners, stores artifacts, exposes basic lineage from dbt artifacts, and integrates Elementary—while keeping dbt’s model DAG inside dbt and product state in PostgreSQL.

## Core Workflows

- Getting started (no projects): guided create project → environment → job.
- Configure environment: warehouse target + runner preference (`local_docker` or `aws_batch`).
- Define and trigger jobs: manual dbt invocation; view status, logs, artifacts.
- Schedule jobs: cron-driven runs.
- Retry / cancel / rerun from run detail.
- Inspect lineage (normalized from `manifest.json`) and Elementary report linked to a run.

## Scope

In scope (v0.1 product surface):

- Projects, environments, jobs, schedules, runs, artifact index, basic lineage UI
- Local Docker and AWS Batch runners behind one contract
- DBOS-backed platform workflows and scheduling
- Required Elementary integration
- Docker Compose packaging including a required local dbt runner image
- Getting started empty state when no projects exist

Out of scope (v0.1):

- Auth / OIDC / RBAC and multi-tenancy
- Custom general-purpose DAG DSL or reimplementing dbt’s model DAG
- Temporal, Kafka, Redis as product dependencies
- Helm / Kubernetes as the primary packaging target
- Replacing Elementary’s own UI
- Embedding dbt inside the API process

## Success Criteria

- An adopter can `docker compose up`, complete Getting started, and complete a manual LocalDocker dbt run with logs, artifacts, and basic lineage visible in the UI.
- Schedules, AWS Batch execution, and Elementary reports work for the same domain model without rewriting core entities.
- Product state lives in PostgreSQL; orchestration and cloud services remain behind adapters.

## Assumptions

- Primary audience is an open-source self-hoster (confirmed in MVP brainstorming).
- “Full cloud parity” for v0.1 means the listed surfaces, not feature-complete competitive parity with commercial dbt Cloud.
- Network exposure is the operator’s responsibility until auth lands.
- GitHub is the forge for this repository’s agent delivery workflow.

## Unknowns

- Exact Elementary co-location vs follow-up invocation preferred by most adopters (implementation detail; product requires the integration either way).
- Whether later multi-team / multi-tenant use should share one deployment or remain intentionally single-operator for longer.
