# dbt Control Plane MVP Design

**Date:** 2026-08-25  
**Status:** Ready for review  
**Approach:** Modular monolith (Approach A)  
**Related:** `docs/session-handoff.md`, agent-delivery workflow on GitHub, marketing landing spec `docs/superpowers/specs/2026-08-28-marketing-landing-design.md`

## Purpose

Design an open-source, self-hostable control plane on top of **dbt Core**, with **Elementary** as a required observability integration, conceptually similar to an open-source dbt Cloud, without unnecessary vendor or infrastructure lock-in.

This document defines the v0.1 MVP boundary, domain model, workflows, interfaces, packaging, and first vertical slice. Implementation follows only after this spec is approved and an implementation plan is written.

## Decisions locked in brainstorming

| Topic | Decision |
|-------|----------|
| Primary audience | Open-source adopter who self-hosts |
| Product ambition | Full cloud-parity surface for v0.1 (projects, environments, jobs, schedules, lineage UI) |
| Architecture | Modular monolith: one deployable, strict internal modules |
| Workflow engine | DBOS (Temporal deferred; escape hatch only if DBOS fails proven needs) |
| Scheduling | DBOS scheduling primitives; schedule definitions CRUD in Postgres |
| Runners in v0.1 | `LocalDockerRunner` and `AWSBatchRunner` |
| Local dbt runner image | **Required** in Docker Compose (not optional) |
| Auth | Single-user / no auth in v0.1 |
| Elementary | Required integration in v0.1 |
| Metadata | Normalize core lineage into Postgres; keep raw artifacts in object storage |
| Packaging | Docker Compose first; Helm deferred |
| Forge / delivery | GitHub (existing agent-delivery spec) |
| Empty UI | Getting started screen when there are no projects |
| Marketing landing | Static `www/` page; not a control-plane screen |

## Product boundary

### Control plane owns

Projects, environments, jobs, schedules, runs, credentials references, artifacts index, coarse platform workflow orchestration, normalized lineage subset, Elementary report linkage, and UI/API.

### dbt Core owns

SQL compilation/execution and its internal model DAG. The control plane invokes dbt (for example `dbt build --select ...`) and consumes artifacts/events. It does not reimplement or execute the model DAG node-by-node.

### Elementary owns

Its own observability/data-quality semantics. The control plane integrates and surfaces reports; Elementary is not the canonical metadata store.

### Marketing landing (not this UI)

Public discovery is a static page at `www/`, specified separately. The control plane does not serve it. Do not implement the landing inside `control-plane/ui/`.

### Architectural principles

1. Avoid vendor lock-in: domain models must not depend on Temporal, Elementary, AWS, or a specific orchestrator.
2. Keep product state in PostgreSQL.
3. Treat orchestration as infrastructure behind a `WorkflowEngine` interface (DBOS backend first).
4. Do not reimplement dbt’s internal DAG.
5. Use OCI containers as the execution boundary.
6. Keep cloud-specific services behind adapters.
7. Use the control-plane **run ID** as the system-wide correlation ID.

## Domain model

| Entity | Responsibility |
|--------|----------------|
| **Project** | Git repo URL, default branch, dbt project path |
| **Environment** | Target profile (e.g. dev/prod), warehouse credentials ref, runner preference |
| **Job** | Named dbt command (`build`, `run`, `test`, select/exclude), linked to project + environment |
| **Schedule** | Cron expression; definition in Postgres; execution registration in DBOS |
| **Run** | Immutable execution record: git SHA/ref, timestamps, runner handle, artifact pointers, correlation ID (= run ID), `dbt_status`, `observability_status` |
| **Artifact** | Object-store reference + type (`manifest`, `run_results`, logs, Elementary report) |
| **Lineage node/edge** | Normalized subset from `manifest.json` (models, sources, tests, dependencies) |

### Run status split

- `dbt_status`: outcome of the dbt invocation.
- `observability_status`: outcome of the Elementary / observability step.
- If Elementary fails after dbt succeeds, keep dbt success visible and mark observability failed (`succeeded_with_warnings` style overall, with explicit split fields).

## Explicit non-goals (v0.1)

- Auth / OIDC / RBAC
- Multi-tenancy
- Custom general-purpose DAG DSL
- Temporal, Kafka, Redis
- Helm / Kubernetes as primary packaging
- Replacing Elementary’s own UI
- Embedding dbt in the API process
- Treating prompts as security boundaries (delivery concerns stay in agent-delivery docs)
- Implementing the marketing landing inside `control-plane/ui/`

## Architecture: modular monolith

```text
control-plane/
  core/            # domain models; no framework/orchestrator imports
    projects/
    environments/
    jobs/
    runs/
    workflows/
  api/             # FastAPI
  orchestration/
    base.py        # WorkflowEngine protocol
    dbos/          # DBOSBackend
  runners/
    base.py        # Runner protocol
    docker.py      # LocalDockerRunner
    aws_batch.py   # AWSBatchRunner
  integrations/
    dbt/
    elementary/
  storage/
    postgres/
    artifacts/     # ArtifactStore protocol + MinIO/S3 adapters
  ui/              # Next.js
```

Single process hosts API + DBOS worker for v0.1. Module boundaries support parallel agent ownership without splitting into multiple services yet.

### Suggested interfaces

```python
class Runner(Protocol):
    async def submit(self, spec: RunSpec) -> RunnerHandle: ...
    async def status(self, handle: RunnerHandle) -> RunnerStatus: ...
    async def cancel(self, handle: RunnerHandle) -> None: ...
    async def logs(self, handle: RunnerHandle, *, since: str | None = None) -> LogCursor: ...

class ArtifactStore(Protocol):
    async def put(self, ...): ...
    async def get(self, ...): ...
    async def list(self, ...): ...

class WorkflowEngine(Protocol):
    async def start(self, ...): ...
    async def cancel(self, ...): ...
    async def retry(self, ...): ...
    async def status(self, ...): ...
```

`RunSpec` includes: image, env, command, git SHA, project path, artifact upload target, run_id correlation, secrets refs (not raw secrets in core).

Core/domain code must never import DBOS, Temporal, AWS SDKs, or Elementary client libraries.

## User workflows

1. Bootstrap: `docker compose up`; open UI.
2. Getting started (no projects): guided create project → environment → job.
3. Configure environment: warehouse target + runner (`local_docker` or `aws_batch`).
4. Define job: dbt command + select/exclude.
5. Manual run: trigger → live status/logs → artifacts → basic lineage.
6. Schedule: attach cron; see next run / history.
7. Retry / cancel / rerun from run detail.
8. Elementary: after dbt, collect/surface report linked to the run.

## Platform workflow (DBOS)

```text
checkout repo @ SHA
  → resolve profile/credentials into runner spec
  → runner.submit(dbt container)
  → wait for completion (durable timer / poll; do not block a worker for full duration)
  → collect artifacts → object store
  → normalize lineage subset into Postgres
  → Elementary step (required)
  → finalize dbt_status + observability_status
```

### DBOS owns vs does not own

| Owns | Does not own |
|------|----------------|
| Durable platform workflows | Product CRUD truth (Postgres domain tables) |
| Cron that starts workflows | dbt model dependency resolution |
| Retries, cancel, recovery of platform steps | Raw warehouse credentials beyond refs |
| Queueing / concurrency limits for runs | UI rendering |

Schedule **definitions** live in Postgres for API/UI CRUD. Create/update upserts DBOS scheduled workflow registration.

Long-running runner waits use DBOS durable sleep/poll (or later webhooks). Exact DBOS APIs are chosen at implementation against current DBOS docs—not spiked against Temporal.

## Artifacts and lineage

| In Postgres | In object store |
|-------------|-----------------|
| Run metadata and split statuses | Full `manifest.json`, `run_results.json`, logs |
| Lineage nodes/edges | Elementary full report payloads |
| Artifact index (type, URI, size, hash) | Large binaries / HTML reports |

UI lineage reads Postgres; drill-down fetches raw artifacts.

## Elementary

Required platform step after dbt. Prefer one documented execution path (same container co-location vs follow-up step). Store report artifact + link on the Run; surface summary in run detail. Not the canonical metadata store.

## API surface (MVP)

- CRUD: projects, environments, jobs, schedules
- Runs: create (manual), get, list, cancel, retry/rerun, logs, artifacts, lineage
- Health / version
- No auth middleware in v0.1; docs assume localhost / private network

## UI screens (MVP)

1. **Getting started** — empty state when there are no projects; guided first setup
2. Projects list + create
3. Project detail — environments, jobs, schedules
4. Job detail — trigger run, schedule editor
5. Runs list + run detail — status (split), logs, artifacts, Elementary summary, retry/cancel
6. Lineage view — project-scoped graph from normalized edges
7. Settings — runner defaults, AWS Batch config presence, Elementary config

## Stack

- Backend/API: Python + FastAPI
- ORM/migrations: SQLAlchemy 2 + Alembic
- Control DB: PostgreSQL
- Frontend: Next.js + TypeScript
- Workflow: DBOS
- Artifacts: S3-compatible (MinIO in Compose) behind adapter
- Telemetry: OpenTelemetry
- dbt execution: dedicated runner container image (required in Compose)
- Auth: deferred (OIDC later)

## Deployment

**Primary:** Docker Compose including:

- API + DBOS worker (same process)
- PostgreSQL
- MinIO
- Next.js UI
- **Local dbt runner image (required)**

AWS Batch is an optional *execution target* when configured; Compose always includes the local runner image so a zero-AWS adopter can run dbt. Batch adapter ships in v0.1 code; AWS credentials are not required to start the stack.

Helm deferred.

## Observability and recovery

- OpenTelemetry on API and workflow activities
- Run ID as correlation ID across logs, artifacts, and runner tags
- Cancel / retry / rerun via `WorkflowEngine`
- Configurable concurrency limit on concurrent runs (small default)
- Worker restart: DBOS recovers in-flight platform workflows

## Implementation milestones

1. Steering bootstrap (`PRODUCT`, `TECH`, `STRUCTURE`, `ROADMAP`, `AGENTS`, ADRs for DBOS, runners, artifacts)
2. Domain + API CRUD + Postgres migrations
3. LocalDockerRunner + one platform workflow (manual run → artifacts → lineage)
4. UI: getting started + project/job/run detail
5. Schedules via DBOS
6. AWSBatchRunner adapter
7. Elementary step + observability status
8. Compose packaging polish + OSS adopter docs

## First vertical slice

Empty Compose stack (including required local dbt runner image) → Getting started → create project + environment → define job → **manual LocalDocker run** → logs + artifacts in UI → basic lineage from `manifest`.

Out of slice (follow milestones 5–7): schedules, AWS Batch execution, Elementary.

## Product-steering follow-through

After this spec is approved, durable truth should be written into:

- `docs/PRODUCT.md`
- `docs/TECH.md`
- `docs/STRUCTURE.md`
- `docs/ROADMAP.md`
- root `AGENTS.md`
- `docs/adr/` for durable decisions (DBOS, runner contract, artifact/lineage strategy)

Do not duplicate the full design into every file; point `AGENTS.md` at these docs.

## Open implementation details (not blockers for this spec)

- Exact DBOS API for durable wait/poll and schedule registration
- Whether Elementary co-runs in the dbt container or as a second invocation
- Minimum warehouse credential secret-ref mechanism for Compose (env file vs mounted secret)

These are resolved during implementation planning against current upstream docs.

## Assumptions

- A single operator runs the stack for their team; network exposure is their responsibility until auth lands.
- “Full cloud parity” for v0.1 means the listed product surfaces, not feature-complete competitive parity with commercial dbt Cloud.
- GitHub remains the forge for this product repository’s agent delivery workflow.

## Non-goals for this design document

- Implementing application code
- Re-comparing DBOS vs Temporal
- Building a delivery-platform coordinator service
