# Roadmap Planning Dry-Run Scenarios

Dry runs simulate roadmap and Linear state. They perform no Linear or repository writes outside `.agent-delivery/runs/`.

## empty-milestone

Approved roadmap contains M1 with deliverables M1-D1 and M1-D2. Linear contains no matching sync keys.
Expected: create one milestone parent and two child tickets in Draft or Needs Planning.

## idempotent-rerun

Approved roadmap and matching draft Linear tickets have identical sync keys and content.
Expected: create nothing, refine nothing, return SYNCED.

## refine-draft

M1-D1 exists in Needs Planning, but its acceptance criteria omit a roadmap-required behavior.
Expected: refine M1-D1 without changing its sync key or state.

## active-ticket-conflict

M1-D1 is Agent Ready and differs from the approved roadmap.
Expected: skip mutation, report an active-ticket conflict, return PARTIAL or BLOCKED.

## duplicate-sync-key

Two Linear tickets contain `Roadmap sync key: M1-D1`.
Expected: make no mutation for M1-D1 and return BLOCKED.

## missing-roadmap-id

An active roadmap deliverable has no stable identifier.
Expected: make no Linear mutations and return BLOCKED.

## milestone-dependency

M2 depends on completion evidence from M1.
Expected: create the dependency edge and do not mark either milestone Agent Ready.

## stale-draft

A draft Linear ticket has sync key M1-D3, but the approved roadmap no longer contains M1-D3.
Expected: report the stale draft; do not delete, cancel, or close it.
