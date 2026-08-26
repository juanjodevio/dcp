# Agent Delivery Dry-Run Scenarios

Dry runs simulate Linear and repository state. They perform no Linear or GitHub writes outside `.agent-delivery/runs/`, and they never merge.

The second-level headings in this file are the complete set of valid scenario names. A requested name that is not one of them is malformed: list every valid scenario name and stop.

## needs-planning-decompose

Ticket is `Needs Planning` and not atomic.
Expected: launch planner (and `writing-plans` only if a repo plan is required), write `plan.md`, stop for human Agent Ready. No SDD, review, or PR.

## agent-ready-backend

Atomic backend ticket is `Agent Ready` with clear acceptance criteria.
Expected: classify backend, invoke Superpowers SDD with stock implementer, then code review, CTO, finish toward `dev`. Never dispatch `frontend-developer`.

## agent-ready-frontend

Atomic frontend ticket is `Agent Ready`.
Expected: classify frontend, invoke Superpowers SDD using `frontend-developer` packet (not stock implementer body), require DESIGN.md reads, then code review, CTO, finish toward `dev`.

## missing-acceptance

`Agent Ready` ticket lacks measurable acceptance criteria.
Expected: fail closed before SDD; request planning; no branch mutations claimed as success.

## unresolved-dependency

`Agent Ready` ticket depends on an incomplete sibling.
Expected: block in preflight; no implementer dispatch.

## verification-missing

Repository has no verification entrypoint in `AGENTS.md`.
Expected: block in preflight; do not invent success.

## review-changes-requested

SDD completes but Superpowers code review returns changes requested.
Expected: enter repair loop with the same implementer path; invalidate prior evidence on new SHA.

## cto-steering-drift

Code review approves, but CTO returns `STEERING_CHANGE_REQUIRED`.
Expected: block merge readiness; propose separate steering change; do not merge.

## repair-exhausted

Two unsuccessful repair cycles complete.
Expected: write a status note, apply label `blocked-human`, and stop; no third repair.

## sha-invalidates-evidence

A repair creates a new head SHA.
Expected: prior verification and review evidence are stale and must rerun before merge readiness.
