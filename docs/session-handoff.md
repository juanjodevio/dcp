# Session Handoff — Open-source dbt Control Plane

## Current goal
Design an open-source, self-hostable control plane on top of **dbt Core** and optionally **Elementary**, conceptually similar to an open-source dbt Cloud, while avoiding unnecessary vendor or infrastructure lock-in.

## Product boundary
The emerging direction is:

- **dbt Core** owns SQL compilation/execution and its internal model DAG.
- **The control plane** owns projects, environments, jobs, schedules, runs, credentials, RBAC, artifacts, and orchestration of coarse workflow steps.
- **Elementary** is an optional observability/data-quality integration, not the canonical metadata store.
- **dbt artifacts** (`manifest.json`, `run_results.json`, etc.) should remain canonical inputs for lineage/run metadata.
- Execution should happen through replaceable runners such as Docker, Kubernetes, AWS Batch, or ECS.

## Current architectural principles

1. **Avoid vendor lock-in.** Self-hostable alone is not enough; core domain models should not depend on Temporal, Elementary, AWS, or another orchestrator.
2. **Keep product state in PostgreSQL.** Projects, environments, jobs, runs, users, and permissions belong to the control plane database.
3. **Treat orchestration as infrastructure.** The workflow engine should be replaceable behind an interface.
4. **Do not reimplement dbt's internal DAG.** Let dbt resolve model dependencies and concurrency internally.
5. **Use OCI containers as the execution boundary.** The control plane should launch dbt through runners rather than embedding dbt in the API process.
6. **Keep cloud-specific services behind adapters.** AWS Batch/S3/Secrets Manager are implementations, not core assumptions.
7. **Use the control-plane run ID as the system-wide correlation ID** across runners, artifacts, telemetry, and observability.

## Stack discussion so far

### Core stack
- Backend/API: **Python + FastAPI**
- Control DB: **PostgreSQL**
- Frontend: **Next.js + TypeScript**
- ORM/migrations: SQLAlchemy 2 + Alembic
- Artifacts: S3-compatible object storage behind an adapter
- Telemetry: OpenTelemetry
- Auth: OIDC
- dbt execution: separate container/process
- Initial runner candidate: AWS Batch

### Temporal
Temporal was considered because it provides durable workflow state, retries, timers, cancellation, task queues, fan-out/fan-in, and worker recovery.

Main concern: adopting Temporal introduces another stateful distributed service to deploy, operate, monitor, upgrade, and back up. It also creates architectural coupling to Temporal's workflow/replay model if domain logic is written directly against its SDK.

If Temporal is used, the intended boundary is:

```text
Our product/domain
    -> WorkflowEngine interface
        -> Temporal backend
            -> worker activities
                -> Runner abstraction
                    -> Docker / K8s / AWS Batch / ECS
                        -> dbt container
```

Core/domain code should never import Temporal.

### DBOS
DBOS was raised as an alternative because it provides durable Python workflows backed directly by PostgreSQL, avoiding a separate workflow server for the basic deployment.

Why it looks attractive:
- Python-native
- Uses PostgreSQL for durable workflow state
- Supports retries, queues, scheduling, concurrency controls, and recovery
- Simpler self-hosted footprint than Temporal

Trade-off:
- Temporal is the more mature heavy-duty distributed workflow system.
- DBOS may be sufficient for coarse dbt control-plane workflows and keeps the installation much simpler.

Decision: **use DBOS for the workflow engine in v0.1**. Do not spend time on a DBOS-vs-Temporal spike. Temporal remains only a future escape hatch if DBOS hits a proven limitation.

## Important design distinction: two DAGs

### dbt DAG
Owned by dbt itself. Example:

```text
staging -> intermediate -> marts -> tests
```

Do not execute this DAG from the control plane. Invoke dbt (`dbt build --select ...`) and consume its artifacts/events.

### Platform workflow DAG
Owned by the control plane. Example:

```text
checkout repo
    -> submit dbt run
        -> wait for runner
            -> collect artifacts
                -> ingest metadata
                    -> Elementary / notifications
```

This is the workflow layer that DBOS or Temporal would own.

## Suggested interfaces

### Runner
```python
class Runner(Protocol):
    async def submit(self, spec): ...
    async def status(self, handle): ...
    async def cancel(self, handle): ...
```

Possible implementations:
- LocalDockerRunner
- KubernetesRunner
- AWSBatchRunner
- ECSRunner

### Artifact store
```python
class ArtifactStore(Protocol):
    async def put(self, ...): ...
    async def get(self, ...): ...
    async def list(self, ...): ...
```

Possible implementations:
- FilesystemArtifactStore
- S3ArtifactStore
- GCSArtifactStore
- AzureBlobArtifactStore

### Workflow engine
```python
class WorkflowEngine(Protocol):
    async def start(self, ...): ...
    async def cancel(self, ...): ...
    async def retry(self, ...): ...
    async def status(self, ...): ...
```

Initial implementation:
- **DBOSBackend**

Future only if requirements force it:
- TemporalBackend
- Native backend

## Suggested repository structure

```text
control-plane/
  core/
    projects/
    environments/
    jobs/
    runs/
    workflows/

  api/
    # FastAPI

  orchestration/
    base.py
    dbos/

  runners/
    base.py
    docker.py
    kubernetes.py
    aws_batch.py

  integrations/
    dbt/
    elementary/

  storage/
    postgres/
    artifacts/

  ui/
    # Next.js
```

## MVP scope currently implied

- Projects
- Environments
- Jobs
- Schedules
- Runs and run history
- Git SHA/ref tracking
- dbt execution through one runner
- Artifact collection
- Basic lineage from dbt artifacts
- Elementary integration as optional observability
- Logs/status UI
- Retry/cancel/rerun

Avoid initially:
- Custom general-purpose DAG DSL
- Kafka
- Redis unless required later
- Kubernetes as a hard dependency
- Rust/Elixir rewrite
- Reimplementing dbt internals

## Open questions for next session

1. How should long-running external runner waits be modeled in DBOS without tying up workers unnecessarily?
2. Should scheduling live in DBOS or in the control-plane database plus a thin scheduler?
3. What is the minimum runner contract needed for Docker, Kubernetes, and AWS Batch parity?
4. What dbt artifacts should be normalized into the control-plane metadata DB vs queried directly from object storage?
5. How much of Elementary should be surfaced directly versus normalized into our own observability model?
6. What is the simplest self-hosted packaging target: Docker Compose first, Helm second?

## Suggested skills for the next agent

- **web research/search** — verify the latest DBOS, dbt Core/Fusion, and Elementary capabilities when implementation details matter.
- **GitHub** — inspect source code and implementation details of DBOS, dbt Core/Fusion, and Elementary when API/behavior details matter.
- **document/spec creation** — once the architecture is chosen, create `SPEC.md` / `ARCHITECTURE.md` / ADRs instead of duplicating the design in chat.

## Immediate next step
**Plan the MVP before implementation.** DBOS is already the chosen workflow engine for v0.1; do not spend time comparing it with Temporal.

The next session should define a concrete MVP plan covering:

- MVP product boundary and explicit non-goals.
- The minimum user workflows the product must support.
- Core domain model: projects, environments, jobs, schedules, runs, and artifacts.
- DBOS workflow responsibilities and boundaries.
- The initial `Runner` contract and which runner ships first.
- dbt execution lifecycle and artifact ingestion.
- Minimum metadata/lineage model derived from dbt artifacts.
- Elementary integration boundary and what remains optional.
- API surface required for the MVP.
- Minimum UI screens and interactions.
- Authentication/RBAC scope for v0.1.
- Local/self-hosted deployment model, preferably Docker Compose first.
- Observability, retries, cancellation, recovery, and concurrency limits.
- Milestones/order of implementation leading to the first usable release.

The MVP plan should end with a **small vertical slice definition** that can be implemented immediately after planning, but implementation itself is not the immediate task.

Temporal should only be revisited if a concrete DBOS limitation appears during implementation or scale testing.
