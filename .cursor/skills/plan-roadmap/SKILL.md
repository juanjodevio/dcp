---
name: plan-roadmap
description: Turns the approved roadmap into Linear projects (milestones) and draft issues (deliverables). Invoke explicitly as /plan-roadmap, /plan-roadmap MILESTONE-ID, or /plan-roadmap DRY-RUN scenario-name.
disable-model-invocation: true
icon: map
color: blue
---

# Plan Roadmap

Turn approved roadmap intent into draft Linear work. Never change roadmap intent or promote work to Agent Ready.

Read [MILESTONE-TEMPLATES.md](MILESTONE-TEMPLATES.md) before planning or mutating Linear. Its authoring forms, parsing patterns, malformed declaration detectors, sync-key exactness rules, and milestone activity rules are binding.

During live and dry runs, the parent workflow must not edit steering docs, ADRs, or application code, and must never commit or push to `main`. The only permitted repository-local writes are:

- the required evidence and reconciliation artifacts under `.agent-delivery/runs/`; and
- the mechanical roadmap-link branch described under "Open the mechanical roadmap-link pull request", which adds only Linear link lines to `docs/ROADMAP.md` (milestone `Linear project:` lines and linked deliverable bullet prefixes).

Dry runs perform no external writes and never create a branch, commit, or pull request.

## Parse the invocation

Accept exactly:

- `/plan-roadmap`
- `/plan-roadmap MILESTONE-ID`
- `/plan-roadmap DRY-RUN scenario-name`

The literal token `DRY-RUN` is reserved and is never a milestone ID. `/plan-roadmap DRY-RUN` without a scenario is malformed.

If malformed, show these forms and stop before loading approved intent, launching the Planner, writing evidence, or calling Linear.

`MILESTONE-ID` must match `^M\d+$` exactly. Reject `m1`, `M`, `M1-D1`, `M1x`, and any value carrying surrounding or embedded whitespace. A milestone argument that matches the form but is absent from the parsed approved roadmap milestone set is BLOCKED: report the requested identifier and every parsed approved milestone identifier, then stop before Planner launch and before any Linear mutation. Validate existence against approved roadmap intent, never against Linear.

For dry runs, read [DRY-RUN-SCENARIOS.md](DRY-RUN-SCENARIOS.md). The second-level headings in that file are the complete set of valid scenario names. If the requested name is not one of them, list every valid scenario name and stop before simulating, writing evidence, or calling Linear. Otherwise simulate only the named scenario, write evidence under `.agent-delivery/runs/roadmap-dry-run-<scenario-name>/`, and perform no external writes.

## Establish roadmap authority

Resolve authority before reading approved intent.

1. List Git remotes.
2. When no `origin` remote exists, the authority mode is `local-main-bootstrap` and the committed local `main` branch is the approved roadmap authority. This is the approved bootstrap exception and applies only while no `origin` remote exists.
3. When an `origin` remote exists, the authority mode is `origin-main`. Fetch `origin/main`, require the local `main` commit to equal `origin/main`, and resolve authority to that commit. Return BLOCKED when the fetch fails or when local `main` and `origin/main` differ in either direction; load no approved intent, launch no Planner, mutate no Linear issue, and open no pull request.

Never treat the working tree, the current branch `HEAD`, an unmerged workspace edit, or a detached scratch commit as authority.

Record the authority mode and the resolved approved roadmap SHA in the Roadmap Coverage Report and the Reconciliation Report.

## Load approved intent

1. Read `docs/ROADMAP.md` from `main` at the resolved authority commit using Git, not an unmerged workspace version.
2. Record the approved roadmap SHA.
3. Read `docs/PRODUCT.md`, `docs/TECH.md`, `docs/DESIGN.md`, `docs/STRUCTURE.md`, `docs/adr/`, and root `AGENTS.md` from the same resolved authority commit.
4. Read the target Linear team key from root `AGENTS.md` under `## Delivery Workflow` using the `Linear team:` pattern in MILESTONE-TEMPLATES.md, which accepts an optional Markdown bullet prefix. Exactly one such line must exist in that section. Record the team key and the exact source line it was parsed from.
5. Parse milestone identifiers from milestone headings and deliverable sync keys with the required parsing patterns and deliverable identity resolution rules in MILESTONE-TEMPLATES.md. Accept em dash, en dash, and hyphen-minus milestone separators. Accept linked deliverable bullets (`[TEAM-<number>](url) outcome`), bootstrap deliverable bullets (`[M<number>-D<number>] outcome`), and indented `-`, `*`, and `+` markers. Apply the malformed declaration detectors in the same file: a declaration candidate that fails its allowed pattern is reported and blocks, and a line that is not a candidate is never parsed as an identifier and never blocks. A `###` heading or a sentence that merely mentions `M<number>`, `[M<number>-D<number>]`, or `[TEAM-<number>]` is not a declaration. For linked deliverables, resolve each Linear issue identifier to its immutable sync key in Linear before duplicate detection, activity derivation, stale detection, or Planner launch.
6. Block duplicate approved roadmap milestone identifiers and duplicate deliverable sync keys on every run, including a milestone-scoped run. Duplicate Linear issue identifiers on linked deliverable bullets also return BLOCKED before Planner launch and before any Linear mutation.
7. Derive each milestone's activity from its Linear references using the milestone activity rules in MILESTONE-TEMPLATES.md. Plan ACTIVE milestones. Generate no fresh drafts for a COMPLETE or NEEDS_HUMAN_RECONCILIATION milestone, and report each one with its referenced ticket identifiers.
8. If a requested milestone ID is supplied, scope planning to that milestone while preserving its dependencies.

Stop before Linear mutation if approved steering is missing, contradictory, lacks stable identifiers, or does not establish the target Linear team key.

## Load current Linear state

Exhaustively retrieve:

1. Every Linear **project** in the configured team (or workspace scope the tools expose) whose description contains `Roadmap sync key:`; and
2. Every Linear **issue** containing a `Roadmap sync key:` value in the configured Linear team.

Use the exact team key loaded from approved root `AGENTS.md`, follow pagination until the API proves there are no more pages, and record the page count plus the terminal no-next-page or `hasNextPage=false` signal. Include each issue's description, state, project assignment, and dependencies.

Linear description search matches substrings, so it returns prefix neighbours such as `M10` for `M1` and `M1-D10` for `M1-D1`. Parse each result's own `Roadmap sync key:` line and keep only exact parsed-key equality matches before duplicate detection, before classification, and inside every pre-create recheck. Never classify or count a match discovered by substring, prefix, or containment. Never read a `Depends on:` or `Project sync key:` value as an issue's own sync key. Record this filtering under `### Exact-key filter proof`.

Build two maps before planning: exact milestone sync key → Linear project, and exact deliverable sync key → Linear issue. If correct team scope or pagination completeness cannot be proven, return BLOCKED and perform no Linear mutation.

Handle existing keys as follows:

- BLOCKED when more than one project or more than one issue claims a key after exact-key filtering;
- BLOCKED when an issue or project description carries zero or more than one `Roadmap sync key:` line;
- SKIP_ACTIVE when exactly one issue is Agent Ready, active, completed, canceled, or otherwise outside Draft and Needs Planning, whether or not it differs from the roadmap; or
- BLOCKED when a required mutation is unsupported by the configured Linear tools.

Record any issue still carrying a milestone sync key `M<number>` (legacy parent epic) under legacy milestone parent issues; do not create new ones. Migration may cancel those epics only when the matching project exists and every deliverable for that milestone is assigned to the project.

Stale detection is global on every run. Even when the invocation scopes planning to one milestone, compare every key in the complete Linear maps to every stable key in the whole approved roadmap, and record every Linear key absent from the approved roadmap as stale, including its issue/project and state.

Never delete, cancel, close, or downgrade work except the explicit legacy-epic cancellation path above.

## Plan

Launch a fresh `planner` custom subagent with the approved roadmap, approved steering, ADRs, repository structure, current Linear map, derived milestone activity, and templates.

Require a Roadmap Coverage Report and one Milestone Plan per selected ACTIVE milestone.

The Planner never produces the Reconciliation Report. This parent workflow owns it.

Do not mutate Linear when any plan verdict is BLOCKED.

## Validate proposed mutations

For every proposed project:

1. Confirm its milestone sync key exists in the approved roadmap.
2. Confirm its name matches `M<number> — milestone name` (or the approved separator variant).
3. Confirm the proposal does not change roadmap intent.

For every proposed issue:

1. Confirm its sync key exists in the approved roadmap.
2. Confirm its state is Draft or Needs Planning.
3. Confirm acceptance criteria and verification are measurable.
4. Confirm project sync key and dependency keys exist.
5. Confirm the proposal does not change roadmap intent.
6. Confirm its milestone is ACTIVE.

Canonical content is the title/name and template-required description content, including the immutable sync key, normalized for line endings and insignificant surrounding whitespace. Allowed relations are the project sync key and dependency sync-key set required by the approved roadmap.

Classify each proposal deterministically, always against exact-key filtered results:

- CREATE only when no exact sync key exists after the exhaustive search. Immediately before the CREATE, search the exact sync key again in the same team, fully paginate the result, re-apply the exact parsed-key filter, and reconcile any exact match instead of creating.
- REFINE only when exactly one Draft or Needs Planning issue exists and its normalized canonical content or allowed relations differ.
- UNCHANGED only when exactly one Draft or Needs Planning issue already matches normalized canonical content and allowed relations and the workflow performs no write for it.
- SKIP_ACTIVE when exactly one issue exists in Agent Ready, active, completed, canceled, or any other state outside Draft and Needs Planning.
- BLOCKED for duplicate roadmap keys, duplicate Linear keys, malformed or repeated sync-key lines, incomplete or unscoped search, ambiguity, or any required unsupported mutation.

## Synchronize Linear

Apply mutations in dependency order:

1. Create missing Linear **projects** for ACTIVE milestones (one project per `M<number>`).
2. Create missing deliverable tickets assigned to their milestone project.
3. Refine matching Draft or Needs Planning tickets (including project assignment when missing).
4. Apply dependency links between deliverable issues.
5. After the matching project exists and all of that milestone's deliverables are assigned to it, cancel any legacy milestone parent issue that still carries `Roadmap sync key: M<number>` (do not cancel deliverables).

Include exactly one stable sync key line in every project and issue description. On deliverable issues, record `Project sync key: M<number>` and dependency references on a separate `Depends on:` line. Never create a parent issue for a milestone.

Do not move any issue to Agent Ready. Do not mutate active or terminal-state issues except the legacy-epic cancellation path above.

Before applying dependency links, inspect and record the exact current Linear tool schema for the relation operation. Apply links only when that schema establishes which issues the operation mutates and every issue actually mutated by that operation is in Draft or Needs Planning. Otherwise classify the proposal as BLOCKED. Never mutate an active or terminal-state issue to establish a dependency relation.

Use the configured Linear tool's idempotency support when available. Before retrying an uncertain write, fetch by exact sync key and reconcile instead of blindly creating.

## Open the mechanical roadmap-link pull request

Run this step only in a live run, only after tickets were created, and only when the authority checks passed.

1. Never commit or push to `main`. Before creating anything, list existing local branches matching `chore/roadmap-link-<short-approved-roadmap-sha>-*`.
   - A matching branch with an open pull request is the run's branch. Reuse it and add to it rather than opening a second one.
   - A matching branch with no open pull request is an orphan from an interrupted run. Reuse it only when it is based on the same resolved authority commit and its existing diff passes the step 4 self-check. Otherwise leave it exactly as it is, report it under `### Roadmap link pull request` as requiring human cleanup, and continue on a fresh branch with a new run identifier.
   - Never delete, reset, rebase, or force-update a roadmap-link branch. A human may be reviewing it.
2. Otherwise create a branch from the resolved authority commit named `chore/roadmap-link-<short-approved-roadmap-sha>-<run-id>`.
3. For each milestone whose project or tickets this run created, add or update roadmap links mechanically:
   - add or update exactly one `Linear project: [M<number> — name](url)` line immediately after the milestone heading when the milestone project was created or first linked;
   - replace a legacy `Linear ticket:` / `Linear tickets:` line in place with the `Linear project:` line when migrating;
   - for each deliverable ticket created, add or replace only the bullet's leading Markdown link so the bullet becomes `- [TEAM-<number>](url) <unchanged outcome text>` (replacing a bootstrap `[M<number>-D<number>]` prefix when present);
   - never add a legacy `Linear ticket:` or `Linear tickets:` line on new writes.
   When links already exist, update only the URL or identifier when the run created a replacement; never rewrite outcome text. Change nothing else: no milestone or deliverable additions, removals, renames, or reordering, no prose edits, no steering or ADR edits, and no application code.
4. Re-read the resulting diff line by line and inspect every added, changed, and removed line:
   - every added or changed line must be a `Linear project:` reference line or a deliverable bullet whose only change is the leading `[TEAM-<number>](url)` link prefix (including bootstrap `[M<number>-D<number>]` → linked replacement);
   - the only permitted removed line is an existing `Linear project:`, legacy `Linear ticket:`, legacy `Linear tickets:`, or bootstrap deliverable prefix that this run replaces in place, and there must be zero removed lines of any other kind;
   - no heading, deliverable outcome text, prose line, or other roadmap text may be deleted or rewritten; and
   - the parsed approved milestone identifier set and deliverable sync-key set must be identical before and after the change.
   If any of these fails, discard the branch changes, open no pull request, and report BLOCKED. Treat a deletion of roadmap intent as BLOCKED even when the run's Linear synchronization succeeded.
5. Open a pull request targeting `main` and leave it for human merge. Never merge it, never enable auto-merge, and never push to `main`.
6. If GitHub is unavailable, unconfigured, or the pull request cannot be created, keep the branch local and unmerged, return PARTIAL when Linear synchronization otherwise succeeded and BLOCKED when it did not, and state the exact setup action, such as adding a GitHub `origin` remote, authenticating the `gh` CLI, and then opening a pull request from the recorded branch into `main`.

Record the branch name, whether it was created or reused, any orphan branch needing human cleanup, the pull request URL or its absence, and the exact human action under `### Roadmap link pull request`.

## Report

Write `.agent-delivery/runs/roadmap-<approved-roadmap-sha>-<utc-timestamp>-<run-id>/reconciliation.md` using the Reconciliation Report template, where `<utc-timestamp>` is `YYYYMMDDTHHMMSSZ`. Never overwrite an existing run directory; if the resolved path already exists, choose a new run identifier. Record the run identifier in the report.

Return:

- SYNCED when every selected roadmap deliverable has exactly one matching current ticket and, when tickets were created, the roadmap-link pull request is open for human merge;
- PARTIAL when stale work exists, a SKIP_ACTIVE issue's normalized canonical content or allowed relations differ from the approved roadmap, a milestone needs human reconciliation, or the roadmap-link pull request could not be opened after otherwise successful synchronization; or
- BLOCKED when ambiguity, duplicate roadmap or Linear keys, unproven authority, unsupported mutations, or steering conflicts prevent safe synchronization.

A SKIP_ACTIVE issue is always no-write. When its normalized canonical content and allowed relations match the approved roadmap, it is informational, does not force PARTIAL, and may contribute to SYNCED.

Apply verdict precedence `BLOCKED` > `PARTIAL` > `SYNCED`. Duplicate roadmap keys, duplicate Linear keys, ambiguity, unproven roadmap authority, incomplete or unscoped search, and unsupported operations force BLOCKED.

List the exact human action for every PARTIAL or BLOCKED result.
