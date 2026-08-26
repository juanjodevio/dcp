# Roadmap Planning Dry-Run Scenarios

Dry runs simulate roadmap and Linear state. They perform no Linear or repository writes outside `.agent-delivery/runs/`, and they never create a branch, commit, or pull request.

The second-level headings in this file are the complete set of valid scenario names. A requested name that is not one of them is malformed: list every valid scenario name and stop before simulating, writing evidence, or calling Linear.

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

## duplicate-roadmap-key

The approved roadmap declares deliverable M1-D2 twice, and the invocation scopes planning to M1.
Expected: block before Planner launch and before any Linear mutation, report both duplicate declarations, and return BLOCKED even though the run is milestone-scoped.

## malformed-declaration

The approved roadmap contains a valid `## M1 — Slice`, a valid `- [M1-D1] outcome`, a heading `### Deliverables for M1`, prose that mentions `[M1-D2]`, a Markdown link `- [M1-D2](https://example.com/m1-d2)`, plus the malformed candidates `## M4` and `- [M1-D9]`.
Expected: `### Deliverables for M1`, the prose mention, and the Markdown link are not declaration candidates and never block. `## M4` and `- [M1-D9]` are candidates that fail their allowed patterns, so the run reports them, makes no Linear mutation, and returns BLOCKED.

## prefix-collision-key

The approved roadmap contains M1 and M1-D1. Linear contains only `Roadmap sync key: M10` and `Roadmap sync key: M1-D10`, plus one issue whose `Depends on:` line names M1-D1.
Expected: substring search results are filtered by exact parsed-key equality, so M10 never satisfies M1, M1-D10 never satisfies M1-D1, and a `Depends on:` reference is never read as an issue's own sync key. Both M1 and M1-D1 classify CREATE, and the required pre-create recheck applies the same exact filter.

## missing-roadmap-id

An active roadmap deliverable has no stable identifier.
Expected: make no Linear mutations and return BLOCKED.

## milestone-dependency

M2 depends on completion evidence from M1. The matching M1 and M2 milestone tickets are both in Needs Planning.
Expected: when the recorded exact current Linear schema proves the relation operation mutates no protected issue, create the dependency edge; otherwise return BLOCKED and create no edge. Never mark either milestone Agent Ready.

## stale-draft

A draft Linear ticket has sync key M1-D3, but the approved roadmap no longer contains M1-D3. The invocation scopes planning to M2.
Expected: report the stale draft even though it belongs to an unselected milestone, because stale detection is global; do not delete, cancel, or close it.

## complete-milestone

Approved roadmap M1 carries `Linear tickets: TEAM-11, TEAM-12`, and both referenced tickets are in a completed state. M2 carries no reference line.
Expected: derive M1 as COMPLETE and generate no fresh drafts for it, derive M2 as ACTIVE and plan it. A canceled, unresolvable, or contradicting reference instead derives NEEDS_HUMAN_RECONCILIATION, generates no fresh drafts, and states the exact human action.

## authority-divergence

An `origin` remote exists and local `main` does not equal `origin/main`, or the `origin/main` fetch fails.
Expected: return BLOCKED in authority mode `origin-main`, load no approved intent, launch no Planner, make no Linear mutation, and open no pull request. The committed local `main` is authority only in `local-main-bootstrap` mode, which requires that no `origin` remote exists.

## link-pr-unavailable

A live run created tickets, but GitHub is not configured or the pull request cannot be created.
Expected: keep the mechanical roadmap-link branch local and unmerged, never commit or push to `main`, return PARTIAL when Linear synchronization otherwise succeeded and BLOCKED when it did not, and state the exact setup action. A dry run only records the pull request a live run would open.

## link-pr-intent-deletion

A live run created tickets and the mechanical roadmap-link branch diff removes a deliverable bullet or other roadmap intent line, not only an in-place `Linear tickets:` replacement.
Expected: the self-check that inspects every added, changed, and removed line fails, the branch changes are discarded, no pull request is opened, and the run returns BLOCKED even when Linear synchronization otherwise succeeded.
