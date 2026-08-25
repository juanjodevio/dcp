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

During live and dry runs, the parent workflow must not edit repository files, steering docs, ADRs, or application code. The only permitted repository-local writes are the required evidence and reconciliation artifacts under `.agent-delivery/runs/`.

## Parse the invocation

Accept exactly:

- `/plan-roadmap`
- `/plan-roadmap MILESTONE-ID`
- `/plan-roadmap DRY-RUN scenario-name`

The literal token `DRY-RUN` is reserved and is never a milestone ID. `/plan-roadmap DRY-RUN` without a scenario is malformed.

If malformed, show these forms and stop before loading approved intent, launching the Planner, writing evidence, or calling Linear.

For dry runs, read [DRY-RUN-SCENARIOS.md](DRY-RUN-SCENARIOS.md), simulate only the named scenario, write evidence under `.agent-delivery/runs/roadmap-dry-run-<scenario-name>/`, and perform no external writes.

## Load approved intent

1. Read `docs/ROADMAP.md` from `main` using Git, not an unmerged workspace version.
2. Record the approved roadmap SHA.
3. Read `docs/PRODUCT.md`, `docs/TECH.md`, `docs/DESIGN.md`, `docs/STRUCTURE.md`, `docs/adr/`, and root `AGENTS.md` from the same approved `main` context.
4. Read the target Linear team key from root `AGENTS.md` under `## Delivery Workflow` in the exact form `Linear team: <team-key>`.
5. Validate milestone and deliverable IDs against MILESTONE-TEMPLATES.md.
6. If a requested milestone ID is supplied, scope planning to that milestone while preserving its dependencies.

Stop before Linear mutation if approved steering is missing, contradictory, lacks stable identifiers, or does not establish the target Linear team key.

## Load current Linear state

Exhaustively retrieve every issue containing a `Roadmap sync key:` value in the configured Linear team. Use the exact team key loaded from approved root `AGENTS.md`, follow pagination until the API proves there are no more pages, and record the page count plus the terminal no-next-page or `hasNextPage=false` signal. Include each issue's description, state, parent, and dependencies.

Build the complete map from sync key to Linear issues before planning. If correct team scope or pagination completeness cannot be proven, return BLOCKED and perform no Linear mutation.

Handle existing keys as follows:

- BLOCKED when more than one issue claims a key;
- SKIP_ACTIVE when exactly one issue is Agent Ready, active, completed, canceled, or otherwise outside Draft and Needs Planning, whether or not it differs from the roadmap; or
- BLOCKED when a required mutation is unsupported by the configured Linear tools.

Compare every key in the complete Linear map to every stable key in the approved roadmap. Record every Linear key absent from the approved roadmap as stale, including its issue and state.

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

Canonical content is the title and template-required description content, including the immutable sync key, normalized for line endings and insignificant surrounding whitespace. Allowed relations are the parent sync key and dependency sync-key set required by the approved roadmap.

Classify each proposal deterministically:

- CREATE only when no exact sync key exists after the exhaustive search. Immediately before the CREATE, search the exact sync key again in the same team and fully paginate the result; reconcile any match instead of creating.
- REFINE only when exactly one Draft or Needs Planning issue exists and its normalized canonical content or allowed relations differ.
- UNCHANGED only when exactly one Draft or Needs Planning issue already matches normalized canonical content and allowed relations and the workflow performs no write for it.
- SKIP_ACTIVE when exactly one issue exists in Agent Ready, active, completed, canceled, or any other state outside Draft and Needs Planning.
- BLOCKED for duplicate keys, incomplete or unscoped search, ambiguity, or any required unsupported mutation.

## Synchronize Linear

Apply mutations in dependency order:

1. Create missing milestone parents.
2. Create missing deliverable tickets.
3. Refine matching Draft or Needs Planning tickets.
4. Apply parent and dependency links.

Include the stable sync key in every description.

Do not move any issue to Agent Ready. Do not mutate active or terminal-state issues.

Before applying parent or dependency links, inspect and record the exact current Linear tool schema for the relation operation. Apply links only when that schema establishes which issues the operation mutates and every issue actually mutated by that operation is in Draft or Needs Planning. Otherwise classify the proposal as BLOCKED. Never mutate an active or terminal-state issue to establish a parent or dependency relation.

Use the configured Linear tool's idempotency support when available. Before retrying an uncertain write, fetch by sync key and reconcile instead of blindly creating.

## Report

Write `.agent-delivery/runs/roadmap-<approved-roadmap-sha>/reconciliation.md` using the Reconciliation Report template.

Return:

- SYNCED when every selected roadmap deliverable has exactly one matching current ticket;
- PARTIAL when stale work exists or a SKIP_ACTIVE issue's normalized canonical content or allowed relations differ from the approved roadmap; or
- BLOCKED when ambiguity, duplicates, unsupported mutations, or steering conflicts prevent safe synchronization.

A SKIP_ACTIVE issue is always no-write. When its normalized canonical content and allowed relations match the approved roadmap, it is informational, does not force PARTIAL, and may contribute to SYNCED.

Apply verdict precedence `BLOCKED` > `PARTIAL` > `SYNCED`. Duplicate keys, ambiguity, incomplete or unscoped search, and unsupported operations force BLOCKED.

List the exact human action for every PARTIAL or BLOCKED result.
