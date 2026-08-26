# Runner and artifact adapters

Status: Accepted
Date: 2026-08-25

## Context And Problem Statement

dbt must run outside the API process, on more than one execution substrate, while artifacts must be stored without baking a single cloud into the domain model.

## Decision Drivers

- OCI container as execution boundary
- Parity between local self-host and AWS Batch
- S3-compatible portability
- Compose must always include a local dbt runner image

## Considered Options

- `Runner` + `ArtifactStore` protocols with LocalDocker + AWS Batch and MinIO/S3 adapters
- Embed dbt in the API process for simplicity
- AWS-only execution and storage

## Decision Outcome

Chosen option: "Runner + ArtifactStore protocols". v0.1 ships `LocalDockerRunner` and `AWSBatchRunner`. Docker Compose **requires** the local dbt runner image. AWS Batch is an optional execution target when configured; AWS credentials are not required to start the stack. Artifacts use an S3-compatible store (MinIO in Compose).

## Consequences

- Good, because core stays cloud-agnostic
- Bad, because two runners increase test matrix in v0.1
- Good, because zero-AWS adopters can still run dbt locally

## Confirmation

Compose files include the local runner image; domain packages do not import AWS SDKs; Batch code lives under `runners/`.

## More Information

- `docs/TECH.md`
- `docs/STRUCTURE.md`
