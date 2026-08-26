# DBOS as v0.1 workflow engine

Status: Accepted
Date: 2026-08-25

## Context And Problem Statement

Platform workflows (checkout → submit run → wait → artifacts → lineage → Elementary) need durable execution, retries, cancellation, and scheduling without reimplementing an orchestrator.

## Decision Drivers

- Self-hosted footprint for open-source adopters
- Python-native stack
- Replaceability (avoid locking domain code to one vendor SDK)
- Avoid a DBOS-vs-Temporal spike delaying MVP

## Considered Options

- DBOS behind a `WorkflowEngine` interface
- Temporal behind the same interface
- Homegrown Postgres job table only

## Decision Outcome

Chosen option: "DBOS behind WorkflowEngine", because it keeps durable workflows on PostgreSQL with a smaller ops footprint. Temporal remains a future backend only if DBOS hits a proven limitation. Domain code must not import DBOS.

Scheduling: DBOS scheduling primitives execute cron; schedule **definitions** remain CRUD entities in Postgres.

## Consequences

- Good, because one less distributed system than Temporal for v0.1
- Bad, because long-wait and schedule APIs must be validated against current DBOS docs during implementation
- Bad, because migrating to Temporal later requires discipline at the WorkflowEngine boundary

## Confirmation

Only `orchestration/dbos/` imports DBOS; schedules are registered from Postgres definitions; no Temporal dependency in v0.1 manifests.

## More Information

- `docs/TECH.md`
- `docs/session-handoff.md`
