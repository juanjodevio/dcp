---
name: plan-roadmap
description: Turns the approved roadmap into dependency-ordered milestones and idempotently creates or refines draft Linear tickets. Invoke explicitly as /plan-roadmap, /plan-roadmap MILESTONE-ID, or /plan-roadmap DRY-RUN scenario-name.
disable-model-invocation: true
icon: map
color: blue
---

# Plan Roadmap

Turn approved roadmap intent into draft Linear work. Never change roadmap intent or promote work to Agent Ready.

Read [MILESTONE-TEMPLATES.md](MILESTONE-TEMPLATES.md) before planning or mutating Linear.

## Parse the invocation

Accept exactly:

- `/plan-roadmap`
- `/plan-roadmap MILESTONE-ID`
- `/plan-roadmap DRY-RUN scenario-name`

If malformed, show these forms and stop.

For dry runs, read [DRY-RUN-SCENARIOS.md](DRY-RUN-SCENARIOS.md), simulate only the named scenario, write evidence under `.agent-delivery/runs/roadmap-dry-run-<scenario-name>/`, and perform no external writes.

## Load approved intent

1. Read `docs/ROADMAP.md` from `main` using Git, not an unmerged workspace version.
2. Record the approved roadmap SHA.
3. Read PRODUCT, TECH, DESIGN, STRUCTURE, ADRs, and root AGENTS.md from the same approved context.
4. Validate milestone and deliverable IDs against MILESTONE-TEMPLATES.md.
5. If a requested milestone ID is supplied, scope planning to that milestone while preserving its dependencies.

Stop before Linear mutation if approved steering is missing, contradictory, or lacks stable identifiers.

## Load current Linear state

Retrieve existing milestone parent issues and deliverable tickets, including description, state, parent, dependencies, and every `Roadmap sync key:` value.

Build a unique map from sync key to Linear issue.

Block a sync key when:

- more than one issue claims it;
- an issue is Agent Ready, active, completed, canceled, or otherwise outside Draft and Needs Planning and differs from the roadmap; or
- the required mutation is unsupported by the configured Linear tools.

Never delete, cancel, close, or downgrade work.

## Plan

Launch a fresh `planner` custom subagent with the approved roadmap, approved steering, ADRs, repository structure, current Linear map, and templates.

Require a Roadmap Coverage Report and one Milestone Plan per selected milestone.

Do not mutate Linear when any plan verdict is BLOCKED.

## Validate proposed mutations

For every proposed issue:

1. Confirm its sync key exists in the approved roadmap.
2. Confirm its state is Draft or Needs Planning.
3. Confirm acceptance criteria and verification are measurable.
4. Confirm parent and dependency keys exist.
5. Confirm the proposal does not change roadmap intent.

Classify each proposal as CREATE, REFINE, UNCHANGED, SKIP_ACTIVE, or BLOCKED.

## Synchronize Linear

Apply mutations in dependency order:

1. Create missing milestone parents.
2. Create missing deliverable tickets.
3. Refine matching Draft or Needs Planning tickets.
4. Apply parent and dependency links.

Include the stable sync key in every description.

Do not move any issue to Agent Ready. Do not mutate active or terminal-state issues.

Use the configured Linear tool's idempotency support when available. Before retrying an uncertain write, fetch by sync key and reconcile instead of blindly creating.

## Report

Write `.agent-delivery/runs/roadmap-<approved-roadmap-sha>/reconciliation.md` using the Reconciliation Report template.

Return:

- SYNCED when every selected roadmap deliverable has exactly one matching current ticket;
- PARTIAL when safe draft mutations succeeded but active or stale work needs human attention; or
- BLOCKED when ambiguity, duplicates, unsupported mutations, or steering conflicts prevent safe synchronization.

List the exact human action for every non-SYNCED result.
