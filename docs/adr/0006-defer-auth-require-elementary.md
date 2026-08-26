# Defer auth; require Elementary in v0.1

Status: Accepted
Date: 2026-08-25

## Context And Problem Statement

What security and observability posture should the first usable release take?

## Decision Drivers

- Fastest path to a useful OSS vertical slice
- Open-source adopter running on private networks
- Observability as part of the Cloud-parity story

## Considered Options

- No auth in v0.1 + Elementary required
- OIDC + RBAC from day one + Elementary optional
- No auth + defer Elementary

## Decision Outcome

Chosen option: "No auth in v0.1; Elementary required". Document localhost/private-network assumptions. Runs expose split `dbt_status` and `observability_status` so dbt success remains visible if Elementary fails.

## Consequences

- Good, because auth complexity does not block the vertical slice
- Bad, because public exposure is unsafe—operators must not bind the stack to the public internet without a later auth release
- Good, because Elementary is a first-class part of the product story, not a docs footnote

## Confirmation

No OIDC middleware in v0.1; Elementary step exists in the platform workflow; UI surfaces observability status separately from dbt status.

## More Information

- `docs/PRODUCT.md`
- `docs/ROADMAP.md`
- `docs/DESIGN.md`
