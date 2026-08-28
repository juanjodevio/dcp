# Roadmap Planning Dry-Run Scenarios

Dry runs simulate roadmap and Linear state. They perform no Linear or repository writes outside `.agent-delivery/runs/`, and they never create a branch, commit, or pull request.

The second-level headings in this file are the complete set of valid scenario names. A requested name that is not one of them is malformed: list every valid scenario name and stop before simulating, writing evidence, or calling Linear.

## empty-milestone

Approved roadmap contains M1 with deliverables M1-D1 and M1-D2. Linear contains no matching sync keys.
Expected: create one Linear **project** for M1 and two deliverable issues in Draft or Needs Planning assigned to that project.

## idempotent-rerun

Approved roadmap and matching Linear project plus draft issues have identical sync keys and content.
Expected: create nothing, refine nothing, return SYNCED.

## refine-draft

M1-D1 exists in Needs Planning, but its acceptance criteria omit a roadmap-required behavior.
Expected: refine M1-D1 without changing its sync key, project assignment, or state.

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

The approved roadmap contains a valid `## M1 — Slice`, a valid bootstrap `- [M1-D1] outcome`, a valid linked `- [TEAM-1](https://linear.app/example/issue/TEAM-1) outcome`, a heading `### Deliverables for M1`, prose that mentions `[M1-D2]`, plus the malformed candidates `## M4`, `- [M1-D9]`, and `- [TEAM-2]`.
Expected: `### Deliverables for M1` and the prose mention are not declaration candidates and never block. `## M4`, `- [M1-D9]`, and `- [TEAM-2]` are candidates that fail their allowed patterns, so the run reports them, makes no Linear mutation, and returns BLOCKED.

## prefix-collision-key

The approved roadmap contains M1 and M1-D1. Linear contains only `Roadmap sync key: M10` (on a project) and `Roadmap sync key: M1-D10` (on an issue), plus one issue whose `Depends on:` line names M1-D1.
Expected: substring search results are filtered by exact parsed-key equality, so M10 never satisfies M1, M1-D10 never satisfies M1-D1, and a `Depends on:` reference is never read as an issue's own sync key. Both M1 (project) and M1-D1 (issue) classify CREATE, and the required pre-create recheck applies the same exact filter.

## missing-roadmap-id

An active roadmap deliverable has no stable identifier.
Expected: make no Linear mutations and return BLOCKED.

## milestone-dependency

M2 depends on completion evidence from M1. Deliverable issues under both projects are in Needs Planning.
Expected: when the recorded exact current Linear schema proves the relation operation mutates no protected issue, create the dependency edge between deliverable issues; otherwise return BLOCKED and create no edge. Never mark either issue Agent Ready. Never model the milestone itself as an issue dependency.

## stale-draft

A draft Linear ticket has sync key M1-D3, but the approved roadmap no longer contains M1-D3. The invocation scopes planning to M2.
Expected: report the stale draft even though it belongs to an unselected milestone, because stale detection is global; do not delete, cancel, or close it.

## complete-milestone

Approved roadmap M1 carries `Linear project: [M1 — Slice](https://linear.app/example/project/m1)` and linked deliverable bullets for TEAM-12 and TEAM-13, and every deliverable issue is in a completed state. M2 carries no project line and uses bootstrap `[M2-D1]` bullets only.
Expected: derive M1 as COMPLETE and generate no fresh drafts for it, derive M2 as ACTIVE and plan it (create project + tickets). A canceled, unresolvable, or contradicting reference instead derives NEEDS_HUMAN_RECONCILIATION, generates no fresh drafts, and states the exact human action.

## authority-divergence

An `origin` remote exists and local `main` does not equal `origin/main`, or the `origin/main` fetch fails.
Expected: return BLOCKED in authority mode `origin-main`, load no approved intent, launch no Planner, make no Linear mutation, and open no pull request. The committed local `main` is authority only in `local-main-bootstrap` mode, which requires that no `origin` remote exists.

## link-pr-unavailable

A live run created projects or tickets, but GitHub is not configured or the pull request cannot be created.
Expected: keep the mechanical roadmap-link branch local and unmerged, never commit or push to `main`, return PARTIAL when Linear synchronization otherwise succeeded and BLOCKED when it did not, and state the exact setup action. A dry run only records the pull request a live run would open.

## link-pr-intent-deletion

A live run created tickets and the mechanical roadmap-link branch diff removes a deliverable bullet, rewrites deliverable outcome text, or changes anything other than permitted link prefixes and `Linear project:` lines.
Expected: the self-check that inspects every added, changed, and removed line fails, the branch changes are discarded, no pull request is opened, and the run returns BLOCKED even when Linear synchronization otherwise succeeded.

## linked-deliverable-resolution

Approved roadmap M1 contains linked deliverable `- [TEAM-12](https://linear.app/example/issue/TEAM-12) outcome text`. Linear issue TEAM-12 carries `Roadmap sync key: M1-D1`.
Expected: resolve the deliverable sync key to M1-D1 from Linear before planning; treat M1-D1 as covered when TEAM-12 matches approved content; never treat TEAM-12 as the sync key itself.

## unresolved-linked-deliverable

Approved roadmap M1 contains linked deliverable `- [TEAM-99](https://linear.app/example/issue/TEAM-99) outcome text`, but TEAM-99 does not exist or carries no deliverable sync key.
Expected: return BLOCKED before Planner launch and before any Linear mutation; report the unresolved identifier and milestone.

## legacy-milestone-parent-migration

Approved roadmap M1 already has deliverable issues. Linear still has a parent epic issue with `Roadmap sync key: M1`, and no Linear project yet carries that key.
Expected: create the M1 project, assign deliverables to it, then cancel the legacy epic only after assignment succeeds; never create a new milestone parent issue; write `Linear project:` (not `Linear ticket:`) on the roadmap-link branch.
