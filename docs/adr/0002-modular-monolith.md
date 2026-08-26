# Modular monolith for v0.1

Status: Accepted
Date: 2026-08-25

## Context And Problem Statement

How should the control plane be packaged and process-separated for the first self-hosted release?

## Decision Drivers

- Simplest Docker Compose story for open-source adopters
- Clear module boundaries for agent-driven parallel work
- Avoid premature multi-service operations burden

## Considered Options

- Modular monolith (API + DBOS worker in one process; strict internal modules)
- Split services (API, worker, UI as separate scalable units from day one)
- Thin API + fat worker

## Decision Outcome

Chosen option: "Modular monolith", because one Compose stack and clear `core/` / `runners/` / `orchestration/` boundaries best match the OSS adopter and agent-delivery goals. Services can split later behind existing protocols.

## Consequences

- Good, because `docker compose up` stays approachable
- Bad, because worker scaling implies scaling the combined unit until a later split

## Confirmation

Deployables remain a single API+worker unit in Compose docs; domain code does not assume separate worker networking.

## More Information

- `docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md`
- `docs/STRUCTURE.md`
