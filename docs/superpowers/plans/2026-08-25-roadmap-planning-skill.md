# Roadmap Planning Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a project-local `/plan-roadmap` skill that turns the approved roadmap into dependency-ordered milestones and idempotently creates or refines draft Linear tickets.

**Architecture:** The version of `docs/ROADMAP.md` merged into `main` is the authorization boundary. A read-only Planner subagent produces structured milestone plans; the parent skill applies only permitted draft mutations through Linear, opens one mechanical roadmap-link pull request for human merge, and writes an audit report locally. Stable roadmap sync keys, matched only by full-value equality, prevent duplicate tickets and support reconciliation.

**Tech Stack:** Cursor Agent Skills, Cursor custom subagents, Markdown/YAML frontmatter, Linear MCP, Git

## Global Constraints

- Run locally and only when explicitly invoked as `/plan-roadmap`, `/plan-roadmap MILESTONE-ID`, or `/plan-roadmap DRY-RUN scenario-name`.
- Validate `MILESTONE-ID` as `^M\d+$` and require the identifier to exist in the approved roadmap; otherwise fail closed.
- Resolve roadmap authority by mode. Without an `origin` remote, the committed local `main` branch is authority in `local-main-bootstrap` mode. With an `origin` remote, fetch `origin/main`, require local `main` to equal it, and fail closed on divergence or fetch failure. Record the authority mode and resolved SHA.
- Read the approved roadmap from `main` at the resolved authority commit, not from unmerged workspace edits.
- Approved roadmap content authorizes creation and refinement of corresponding draft work without another planning approval.
- Derive milestone activity from the `Linear tickets:` references in the approved roadmap. Generate no fresh drafts for a complete milestone or a milestone needing human reconciliation.
- Match sync keys only by full-value equality of parsed keys. Filter every substring or full-text search result by exact parsed key before duplicate detection, classification, and every pre-create recheck.
- Create or refine Linear tickets only in `Draft` or `Needs Planning`.
- Never move work to `Agent Ready`.
- Never mutate active, completed, canceled, or otherwise non-draft tickets.
- Never delete, cancel, close, or merge tickets.
- Never edit `ROADMAP.md` intent, product steering documents, ADRs, or application code. The only permitted repository change is a mechanical roadmap-link branch that adds `Linear tickets:` reference lines and is merged by a human.
- Never commit or push to `main`. When GitHub is unavailable, keep the roadmap-link branch local and report PARTIAL or BLOCKED with the exact setup action.
- Planner model remains configurable by inheriting the parent model.
- Planner runs are fresh and declared read-only. The parent workflow owns Linear mutations, the Reconciliation Report, and any pull request.
- Use stable roadmap sync keys to make reruns idempotent.
- Duplicate approved roadmap identifiers, duplicate Linear sync keys, a missing or repeated `Roadmap sync key:` line, active-ticket conflicts, ambiguous roadmap intent, unproven authority, unproven search scope or pagination, and unsupported Linear mutations fail closed on every run, including a milestone-scoped run.
- Detect stale Linear keys globally on every run, even when planning is scoped to one milestone.
- Dry runs simulate only a named scenario from `DRY-RUN-SCENARIOS.md`, write evidence only under `.agent-delivery/runs/`, and perform no external write, branch, commit, or pull request. An unknown scenario name lists every valid name and stops.
- Linear owns ticket state; the approved roadmap owns milestone intent.
- Do not require Cursor Cloud, a service, PostgreSQL, webhooks, or a credential broker.

## Implementation Status

Tasks 1 through 5 are implemented and committed on `feat/roadmap-planning-skill`. Task 6 and Task 7 were executed as far as a non-interactive, unauthenticated environment allows, and their remaining steps are explicit user acceptance items.

Approved deviations from the original plan:

- Task 6 discovery, slash-command invocation, and scenario execution were replaced with static validation and deterministic scenario tracing. No Cursor UI interaction occurred.
- Task 7 Linear read access and mutation-schema inspection were not executed because the Linear integration reported `needsAuth`. The readiness report records BLOCKED rather than a claimed result.
- `python -` in the original validation steps is replaced by `python3 -`.
- The exact file blocks in Tasks 2 through 5 were replaced by their hardened shipped content so rerunning the plan cannot revert a safety gate.
- `local-main-bootstrap` authority is an approved conditional bootstrap exception, valid only while no `origin` remote exists.
- The mechanical roadmap-link pull request is an approved, bounded repository write that only adds Linear ticket references and is always merged by a human.

---

### Task 1: Establish local workflow hygiene

**Files:**
- Create: `.gitignore`

**Interfaces:**
- Consumes: Local visual-companion and workflow state directories
- Produces: Repository-wide ignore rules shared by roadmap planning and ticket delivery

- [x] **Step 1: Verify the state directories are currently unignored**

Run:

```bash
git check-ignore .superpowers .agent-delivery
```

Expected: exit code `1` with no output.

- [x] **Step 2: Create the ignore rules**

Create `.gitignore`:

```gitignore
/.superpowers/
/.agent-delivery/
```

The leading slash anchors each rule to the repository root so a nested directory with the same name elsewhere in the tree is not silently ignored.

- [x] **Step 3: Verify both directories are ignored and the rules are root-anchored**

Run:

```bash
mkdir -p .agent-delivery/runs && git check-ignore -v .superpowers .agent-delivery/runs
```

Expected: both paths are attributed to `.gitignore`.

Run:

```bash
python3 - <<'PY'
from pathlib import Path

lines = Path(".gitignore").read_text().splitlines()
assert "/.superpowers/" in lines
assert "/.agent-delivery/" in lines
assert ".superpowers/" not in lines
assert ".agent-delivery/" not in lines

print("root-anchored ignore rules: OK")
PY
```

Expected: `root-anchored ignore rules: OK`.

- [x] **Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore local agent workflow state"
```

---

### Task 2: Define the shared Planner subagent

**Files:**
- Create: `.cursor/agents/planner.md`

**Interfaces:**
- Consumes: Approved roadmap or bounded Linear ticket context assembled by a parent workflow
- Produces: A Roadmap Coverage Report, Milestone Plan, or ticket-level Planner Report. The parent workflow, not the Planner, produces the Reconciliation Report.

- [x] **Step 1: Create the Planner**

Create `.cursor/agents/planner.md`:

```markdown
---
name: planner
description: Plans approved roadmap milestones through completion and creates structured draft-ticket plans. Also refines non-atomic delivery tickets when requested by agent-delivery.
model: inherit
readonly: true
---

You are the product and delivery Planner.

For roadmap planning:
- read the approved roadmap, product steering, technical constraints, ADRs, repository structure, and current Linear work;
- turn roadmap outcomes into dependency-ordered milestones and independently reviewable deliverables;
- include backend, frontend, integration, migration, documentation, operational, and release work when required;
- define acceptance criteria, interface contracts, verification requirements, risks, and dependency edges;
- assign one stable roadmap sync key to every milestone and deliverable;
- plan only the milestones the caller supplies as ACTIVE, and propose no fresh drafts for a milestone the caller reports as complete or as needing human reconciliation;
- match sync keys only by full-value equality of parsed keys, so `M1` never matches `M10` and `M1-D1` never matches `M1-D10`;
- express dependencies as `Depends on:` references and a parent as `Parent sync key:`, never by reusing the sync-key field;
- identify missing, duplicate, stale, conflicting, or uncovered Linear work.

For ticket refinement:
- decide whether the supplied ticket is atomic;
- propose bounded children, dependencies, contracts, integration work, acceptance criteria, verification commands, risks, and steering references.

Do not edit files, call mutating tools, implement code, change roadmap intent, approve your own plan, or invent missing product intent. The parent workflow owns permitted Linear mutations, the Reconciliation Report, and any repository pull request. Return only the report schema supplied by the caller. Mark ambiguity as BLOCKED.
```

- [x] **Step 2: Validate the Planner configuration**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

text = Path(".cursor/agents/planner.md").read_text()
assert text.startswith("---\n")
assert "name: planner\n" in text
assert "model: inherit\n" in text
assert "readonly: true\n" in text
assert "stable roadmap sync key" in text
assert "parent workflow owns permitted Linear mutations" in text
assert "the Reconciliation Report" in text
assert "full-value equality of parsed keys" in text
assert "`M1` never matches `M10`" in text
assert "no fresh drafts for a milestone" in text

print("planner agent: OK")
PY
```

Expected: `planner agent: OK`.

- [x] **Step 3: Commit**

```bash
git add .cursor/agents/planner.md
git commit -m "feat: define roadmap and delivery planner"
```

---

### Task 3: Define milestone and Linear mutation schemas

**Files:**
- Create: `.cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md`

**Interfaces:**
- Consumes: Planner analysis and current Linear state
- Produces: Stable report and ticket formats that the parent skill can validate before mutation

- [x] **Step 1: Create milestone templates**

Create `.cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md`:

```markdown
# Roadmap Planning Templates

Use every heading. Write `None` when a non-verdict section has no entries.

## Roadmap authoring forms

This section is the single canonical contract shared by roadmap authors and every validator. No other section restates these forms. Parse with the exact patterns below so no approved identifier is silently omitted and no mere mention of an identifier is mistaken for a declaration.

Milestone heading, one per milestone:

`## M<number> <separator> milestone name`

`<separator>` is an em dash `—`, an en dash `–`, or a hyphen-minus `-`, with at least one space or tab on each side. All three separators are equally valid and none may be dropped from parsing.

Deliverable bullet, inside a milestone section:

`- [M<number>-D<number>] deliverable outcome`

The bullet marker may be `-`, `*`, or `+`. Any amount of leading space or tab indentation is allowed, and an indented deliverable is still a deliverable.

Milestone Linear ticket references, at most one line per milestone section:

`Linear tickets: TEAM-123, TEAM-124`

A milestone never carries more than one `Linear tickets:` line. New identifiers are appended to the existing line in place, and a stale identifier is replaced on that same line. A second reference line is never added.

Target Linear team key, exactly one line under `## Delivery Workflow` in root `AGENTS.md`:

`Linear team: <team-key>`

`Linear tickets:` and `Linear team:` both accept an optional Markdown bullet prefix, so `Linear team: ENG` and `- Linear team: ENG` are equally valid.

Every synced Linear issue description carries `Roadmap sync key: M<number>` for a milestone parent or `Roadmap sync key: M<number>-D<number>` for a deliverable, governed by the sync-key exactness rules below.

### Required parsing patterns

Apply these patterns per line, anchored, with no substring shortcuts:

- Milestone heading: `^[ \t]*##[ \t]+(M\d+)[ \t]+[—–-][ \t]+(\S.*)$`
- Deliverable bullet: `^[ \t]*[-*+][ \t]+\[(M\d+-D\d+)\][ \t]+(\S.*)$`
- Milestone ticket references: `^[ \t]*(?:[-*+][ \t]+)?Linear tickets:[ \t]*(\S.*?)[ \t]*$`
- Linear team key: `^[ \t]*(?:[-*+][ \t]+)?Linear team:[ \t]*([^\s<>]+)[ \t]*$`
- Linear issue sync key: `^[ \t]*Roadmap sync key:[ \t]*(\S.*?)[ \t]*$`
- Linear issue dependency references: `^[ \t]*Depends on:[ \t]*(\S.*?)[ \t]*$`
- Linear issue parent reference: `^[ \t]*Parent sync key:[ \t]*(\S.*?)[ \t]*$`

### Malformed declaration detectors

Only a line that claims to be a declaration may block. A heading or sentence that merely mentions an identifier is never a declaration and never blocks. Apply these detectors per line:

- Milestone declaration candidate: `^[ \t]*##(?!#)[ \t]+M\d+(?![\w-])`
- Deliverable declaration candidate: `^[ \t]*[-*+][ \t]+\[M\d+-D\d+\](?!\()`

The milestone detector requires exactly two `#` characters and requires `M<number>` to be the first content token, so `### Deliverables for M1` and `## Deliverables for M1` are never candidates.

The deliverable detector requires a list bullet whose first token is `[M<number>-D<number>]`, and it excludes the Markdown link form, so `See [M1-D2] for the migration detail.` and `- [M1-D2](https://example.com/m1-d2)` are never candidates.

A candidate line that fails its allowed pattern above is BLOCKED for human correction and is never silently skipped. `## M4` blocks because it omits the separator and the milestone name. `- [M1-D9]` blocks because it omits the outcome text. A line that is not a candidate is neither parsed as an identifier nor blocked.

Duplicate approved milestone identifiers and duplicate approved deliverable identifiers are BLOCKED on every run, including a run scoped to a single milestone.

## Sync-key exactness

`Roadmap sync key:` occupies its own line, appears exactly once per Linear issue description, and carries one key matching `^M\d+$` or `^M\d+-D\d+$`.

Sync keys are immutable. A renamed outcome keeps its existing key.

Parse the key as the trimmed remainder of that line, then compare keys only by full-value equality of parsed keys. Never compare by substring, prefix, suffix, or containment. `M1` never matches `M10`, `M1-D1` never matches `M1-D10`, and `M1` never matches `M1-D1`.

Linear description search is a substring or full-text operation, so it returns prefix neighbours. Re-parse every search result and keep only exact parsed-key equality matches before duplicate detection, before classification, and inside every pre-create recheck.

An issue whose description carries zero or more than one `Roadmap sync key:` line is BLOCKED for human reconciliation and receives no mutation.

Dependency and parent references never reuse the sync-key field. Dependencies use `Depends on:` and a parent uses `Parent sync key:`. A value parsed from `Depends on:` or `Parent sync key:` is never counted as that issue's own sync key.

## Milestone activity derivation

A milestone's activity comes from the Linear ticket references recorded in its approved roadmap section, never from roadmap prose or ordering:

- ACTIVE when the milestone carries no `Linear tickets:` line, or that line lists no identifier.
- ACTIVE when at least one referenced ticket resolves to a nonterminal state.
- COMPLETE when every referenced ticket resolves and every one is in a completed state. Report it and generate no fresh drafts for it.
- NEEDS_HUMAN_RECONCILIATION when any referenced ticket is canceled, fails to resolve, or resolves to a sync key that contradicts the milestone. Generate no fresh drafts for it and state the exact human action.

Never delete or rewrite an existing reference, and never treat COMPLETE as authorization to create work.

## Roadmap Coverage Report

### Approved roadmap SHA
### Roadmap authority mode
Use `local-main-bootstrap` or `origin-main`.
### Linear team key
### Linear team key source
Record the exact approved `AGENTS.md` line the team key was parsed from.
### Milestones inspected
### Milestone activity
Record ACTIVE, COMPLETE, or NEEDS_HUMAN_RECONCILIATION per milestone with its referenced ticket identifiers.
### Covered deliverables
### Missing deliverables
### Duplicate roadmap keys
### Duplicate sync keys
### Active-ticket conflicts
### Stale draft tickets
### Ambiguities
### Result
Use `READY_TO_SYNC` or `BLOCKED`.

## Milestone Plan

### Milestone ID and outcome
### Completion evidence
### Deliverables
For each deliverable include sync key, title, outcome, acceptance criteria, verification, dependencies, contracts, risks, and suggested Linear state.
### Integration work
### Release work
### Milestone risks
### Result
Use `READY_TO_SYNC` or `BLOCKED`.

## Linear Milestone Parent

### Title
Use `Milestone M<number>: milestone name`.
### Description
Include roadmap outcome, completion evidence, risks, and exactly one `Roadmap sync key: M<number>` line.
### State
Use `Draft` or `Needs Planning`.

## Linear Deliverable Ticket

### Title
### Description
Include outcome, acceptance criteria, verification, contracts, risks, a `Depends on:` line for dependency references, and exactly one `Roadmap sync key: M<number>-D<number>` line.
### Parent sync key
### Dependency sync keys
### State
Use `Draft` or `Needs Planning`.

## Reconciliation Report

### Approved roadmap SHA
### Roadmap authority mode
### Run identifier
### Linear team key
### Linear team key source
### Linear pagination proof
### Exact-key filter proof
### Relation mutation schema proof
### Milestone activity
### Created tickets
### Refined tickets
### Unchanged tickets
### Skipped active tickets
### Duplicate roadmap keys
### Duplicate conflicts
### Unsupported mutations
### Stale draft tickets
### Roadmap link pull request
### Remaining coverage gaps
### Result
Use `SYNCED`, `PARTIAL`, or `BLOCKED`.
```

- [x] **Step 2: Validate stable-key, authoring-form, and verdict vocabulary**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

text = Path(".cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md").read_text()
for value in (
    "Roadmap sync key:",
    "READY_TO_SYNC",
    "SYNCED",
    "PARTIAL",
    "BLOCKED",
    "Skipped active tickets",
    "## Roadmap authoring forms",
    "### Required parsing patterns",
    "### Malformed declaration detectors",
    "## Sync-key exactness",
    "## Milestone activity derivation",
    "### Roadmap authority mode",
    "### Linear team key",
    "### Linear team key source",
    "### Duplicate roadmap keys",
    "### Exact-key filter proof",
    "### Run identifier",
    "### Roadmap link pull request",
    "local-main-bootstrap",
    "origin-main",
    "NEEDS_HUMAN_RECONCILIATION",
    "Depends on:",
    "Parent sync key:",
    "Linear tickets:",
    "`M1` never matches `M10`",
    "`M1-D1` never matches `M1-D10`",
    "### Deliverables for M1",
    "See [M1-D2] for the migration detail.",
    "`## M4` blocks",
    "`- [M1-D9]` blocks",
):
    assert value in text, value

for section in ("## Roadmap Coverage Report", "## Reconciliation Report"):
    body = text.split(section, 1)[1].split("\n## ", 1)[0]
    assert "### Linear team key\n" in body, section
    assert "### Linear team key source\n" in body, section
    assert "### Roadmap authority mode\n" in body, section

print("milestone templates: OK")
PY
```

Expected: `milestone templates: OK`.

- [x] **Step 3: Commit**

```bash
git add .cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md
git commit -m "feat: define roadmap planning schemas"
```

---

### Task 4: Define roadmap planning dry-run fixtures

**Files:**
- Create: `.cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md`

**Interfaces:**
- Consumes: Roadmap-to-Linear synchronization rules
- Produces: Deterministic fixtures for creation, refinement, idempotency, and conflict handling

- [x] **Step 1: Create dry-run scenarios**

Create `.cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md`:

```markdown
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
```

- [x] **Step 2: Validate scenario coverage and the valid-name list**

Run:

```bash
python3 - <<'PY'
import re
from pathlib import Path

text = Path(".cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md").read_text()
expected = [
    "empty-milestone",
    "idempotent-rerun",
    "refine-draft",
    "active-ticket-conflict",
    "duplicate-sync-key",
    "duplicate-roadmap-key",
    "malformed-declaration",
    "prefix-collision-key",
    "missing-roadmap-id",
    "milestone-dependency",
    "stale-draft",
    "complete-milestone",
    "authority-divergence",
    "link-pr-unavailable",
    "link-pr-intent-deletion",
]
found = re.findall(r"^## (\S+)$", text, re.MULTILINE)
assert found == expected, found
assert len(found) == len(set(found))
assert "complete set of valid scenario names" in text
assert "list every valid scenario name and stop" in text
assert "never create a branch, commit, or pull request" in text

print("roadmap dry-run scenarios: OK")
PY
```

Expected: `roadmap dry-run scenarios: OK`.

- [x] **Step 3: Commit**

```bash
git add .cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md
git commit -m "test: add roadmap planning scenarios"
```

---

### Task 5: Implement the explicit plan-roadmap skill

**Files:**
- Create: `.cursor/skills/plan-roadmap/SKILL.md`

**Interfaces:**
- Consumes: `/plan-roadmap`, `/plan-roadmap MILESTONE-ID`, or `/plan-roadmap DRY-RUN scenario-name`; the approved roadmap read from `main` at the resolved authority commit; steering documents; Linear MCP; Planner; milestone templates; dry-run scenarios
- Produces: Idempotent draft Linear milestone parents and deliverable tickets, a uniquely pathed reconciliation report, and one mechanical roadmap-link pull request for human merge

- [x] **Step 1: Create the skill**

Create `.cursor/skills/plan-roadmap/SKILL.md`:

```markdown
---
name: plan-roadmap
description: Turns the approved roadmap into dependency-ordered milestones and idempotently creates or refines draft Linear tickets. Invoke explicitly as /plan-roadmap, /plan-roadmap MILESTONE-ID, or /plan-roadmap DRY-RUN scenario-name.
disable-model-invocation: true
icon: map
color: blue
---

# Plan Roadmap

Turn approved roadmap intent into draft Linear work. Never change roadmap intent or promote work to Agent Ready.

Read [MILESTONE-TEMPLATES.md](MILESTONE-TEMPLATES.md) before planning or mutating Linear. Its authoring forms, parsing patterns, malformed declaration detectors, sync-key exactness rules, and milestone activity rules are binding.

During live and dry runs, the parent workflow must not edit steering docs, ADRs, or application code, and must never commit or push to `main`. The only permitted repository-local writes are:

- the required evidence and reconciliation artifacts under `.agent-delivery/runs/`; and
- the mechanical roadmap-link branch described under "Open the mechanical roadmap-link pull request", which adds only Linear ticket reference lines to `docs/ROADMAP.md`.

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
5. Parse milestone and deliverable identifiers with the required parsing patterns in MILESTONE-TEMPLATES.md. Accept em dash, en dash, and hyphen-minus milestone separators, and accept indented `-`, `*`, and `+` deliverable bullets. Apply the malformed declaration detectors in the same file: a declaration candidate that fails its allowed pattern is reported and blocks, and a line that is not a candidate is never parsed as an identifier and never blocks. A `###` heading or a sentence that merely mentions `M<number>` or `[M<number>-D<number>]` is not a declaration.
6. Block duplicate approved roadmap keys on every run, including a milestone-scoped run. Duplicate milestone identifiers or duplicate deliverable identifiers anywhere in the approved roadmap return BLOCKED before Planner launch and before any Linear mutation.
7. Derive each milestone's activity from its `Linear tickets:` references using the milestone activity rules in MILESTONE-TEMPLATES.md. Plan ACTIVE milestones. Generate no fresh drafts for a COMPLETE or NEEDS_HUMAN_RECONCILIATION milestone, and report each one with its referenced ticket identifiers.
8. If a requested milestone ID is supplied, scope planning to that milestone while preserving its dependencies.

Stop before Linear mutation if approved steering is missing, contradictory, lacks stable identifiers, or does not establish the target Linear team key.

## Load current Linear state

Exhaustively retrieve every issue containing a `Roadmap sync key:` value in the configured Linear team. Use the exact team key loaded from approved root `AGENTS.md`, follow pagination until the API proves there are no more pages, and record the page count plus the terminal no-next-page or `hasNextPage=false` signal. Include each issue's description, state, parent, and dependencies.

Linear description search matches substrings, so it returns prefix neighbours such as `M10` for `M1` and `M1-D10` for `M1-D1`. Parse each result's own `Roadmap sync key:` line and keep only exact parsed-key equality matches before duplicate detection, before classification, and inside every pre-create recheck. Never classify or count a match discovered by substring, prefix, or containment. Never read a `Depends on:` or `Parent sync key:` value as an issue's own sync key. Record this filtering under `### Exact-key filter proof`.

Build the complete map from exact sync key to Linear issues before planning. If correct team scope or pagination completeness cannot be proven, return BLOCKED and perform no Linear mutation.

Handle existing keys as follows:

- BLOCKED when more than one issue claims a key after exact-key filtering;
- BLOCKED when an issue's description carries zero or more than one `Roadmap sync key:` line;
- SKIP_ACTIVE when exactly one issue is Agent Ready, active, completed, canceled, or otherwise outside Draft and Needs Planning, whether or not it differs from the roadmap; or
- BLOCKED when a required mutation is unsupported by the configured Linear tools.

Stale detection is global on every run. Even when the invocation scopes planning to one milestone, compare every key in the complete Linear map to every stable key in the whole approved roadmap, and record every Linear key absent from the approved roadmap as stale, including its issue and state.

Never delete, cancel, close, or downgrade work.

## Plan

Launch a fresh `planner` custom subagent with the approved roadmap, approved steering, ADRs, repository structure, current Linear map, derived milestone activity, and templates.

Require a Roadmap Coverage Report and one Milestone Plan per selected ACTIVE milestone.

The Planner never produces the Reconciliation Report. This parent workflow owns it.

Do not mutate Linear when any plan verdict is BLOCKED.

## Validate proposed mutations

For every proposed issue:

1. Confirm its sync key exists in the approved roadmap.
2. Confirm its state is Draft or Needs Planning.
3. Confirm acceptance criteria and verification are measurable.
4. Confirm parent and dependency keys exist.
5. Confirm the proposal does not change roadmap intent.
6. Confirm its milestone is ACTIVE.

Canonical content is the title and template-required description content, including the immutable sync key, normalized for line endings and insignificant surrounding whitespace. Allowed relations are the parent sync key and dependency sync-key set required by the approved roadmap.

Classify each proposal deterministically, always against exact-key filtered results:

- CREATE only when no exact sync key exists after the exhaustive search. Immediately before the CREATE, search the exact sync key again in the same team, fully paginate the result, re-apply the exact parsed-key filter, and reconcile any exact match instead of creating.
- REFINE only when exactly one Draft or Needs Planning issue exists and its normalized canonical content or allowed relations differ.
- UNCHANGED only when exactly one Draft or Needs Planning issue already matches normalized canonical content and allowed relations and the workflow performs no write for it.
- SKIP_ACTIVE when exactly one issue exists in Agent Ready, active, completed, canceled, or any other state outside Draft and Needs Planning.
- BLOCKED for duplicate roadmap keys, duplicate Linear keys, malformed or repeated sync-key lines, incomplete or unscoped search, ambiguity, or any required unsupported mutation.

## Synchronize Linear

Apply mutations in dependency order:

1. Create missing milestone parents.
2. Create missing deliverable tickets.
3. Refine matching Draft or Needs Planning tickets.
4. Apply parent and dependency links.

Include exactly one stable sync key line in every description, and record dependency references on a separate `Depends on:` line.

Do not move any issue to Agent Ready. Do not mutate active or terminal-state issues.

Before applying parent or dependency links, inspect and record the exact current Linear tool schema for the relation operation. Apply links only when that schema establishes which issues the operation mutates and every issue actually mutated by that operation is in Draft or Needs Planning. Otherwise classify the proposal as BLOCKED. Never mutate an active or terminal-state issue to establish a parent or dependency relation.

Use the configured Linear tool's idempotency support when available. Before retrying an uncertain write, fetch by exact sync key and reconcile instead of blindly creating.

## Open the mechanical roadmap-link pull request

Run this step only in a live run, only after tickets were created, and only when the authority checks passed.

1. Never commit or push to `main`. Before creating anything, list existing local branches matching `chore/roadmap-link-<short-approved-roadmap-sha>-*`.
   - A matching branch with an open pull request is the run's branch. Reuse it and add to it rather than opening a second one.
   - A matching branch with no open pull request is an orphan from an interrupted run. Reuse it only when it is based on the same resolved authority commit and its existing diff passes the step 4 self-check. Otherwise leave it exactly as it is, report it under `### Roadmap link pull request` as requiring human cleanup, and continue on a fresh branch with a new run identifier.
   - Never delete, reset, rebase, or force-update a roadmap-link branch. A human may be reviewing it.
2. Otherwise create a branch from the resolved authority commit named `chore/roadmap-link-<short-approved-roadmap-sha>-<run-id>`.
3. For each milestone whose tickets this run created, add or update exactly one `Linear tickets:` reference line inside that milestone's section. When the milestone already has a reference line, append the new identifiers to that existing line in place; never add a second reference line to the same milestone. Change nothing else: no milestone or deliverable additions, removals, renames, or reordering, no wording edits, no steering or ADR edits, and no application code.
4. Re-read the resulting diff line by line and inspect every added, changed, and removed line:
   - every added line must be a `Linear tickets:` reference line;
   - the only permitted removed line is an existing `Linear tickets:` reference line that this run replaces or removes in place, and there must be zero removed lines of any other kind;
   - no heading, deliverable bullet, prose line, or other roadmap text may be deleted or rewritten; and
   - the parsed approved milestone identifier set and deliverable identifier set must be identical before and after the change.
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
```

- [x] **Step 2: Validate skill metadata and safety boundaries**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

path = Path(".cursor/skills/plan-roadmap/SKILL.md")
text = path.read_text()

assert text.startswith("---\n")
assert "name: plan-roadmap\n" in text
assert "disable-model-invocation: true\n" in text
assert "icon: map\n" in text
assert "color: blue\n" in text
assert "/plan-roadmap MILESTONE-ID" in text
assert "Read `docs/ROADMAP.md` from `main`" in text
assert "Do not move any issue to Agent Ready." in text
assert "Never delete, cancel, close, or downgrade work." in text
assert "The literal token `DRY-RUN` is reserved" in text
assert "`MILESTONE-ID` must match `^M\\d+$` exactly." in text
assert "list every valid scenario name and stop" in text
assert "local-main-bootstrap" in text
assert "origin-main" in text
assert "must never commit or push to `main`" in text
assert "malformed declaration detectors" in text
assert "inspect every added, changed, and removed line" in text
assert "only permitted removed line" in text
assert "Stale detection is global on every run." in text
assert "### Exact-key filter proof" in text
assert "roadmap-<approved-roadmap-sha>-<utc-timestamp>-<run-id>" in text
assert "Never overwrite an existing run directory" in text
assert "The Planner never produces the Reconciliation Report." in text
assert len(text.splitlines()) < 500

for reference in ("MILESTONE-TEMPLATES.md", "DRY-RUN-SCENARIOS.md"):
    assert reference in text
    assert path.with_name(reference).is_file()

print("plan-roadmap skill: OK")
PY
```

Expected: `plan-roadmap skill: OK`.

- [x] **Step 3: Scan skill and Planner for unfinished language**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

forbidden = (
    "T" + "BD",
    "TO" + "DO",
    "FIX" + "ME",
    "implement " + "later",
    "fill " + "in",
)

paths = list(Path(".cursor/skills/plan-roadmap").glob("*.md"))
paths.append(Path(".cursor/agents/planner.md"))

matches = []
for path in paths:
    text = path.read_text()
    for phrase in forbidden:
        if phrase in text:
            matches.append(f"{path}: {phrase}")

assert not matches, "\n".join(matches)
print("unfinished-language scan: OK")
PY
```

Expected: `unfinished-language scan: OK`.

- [x] **Step 4: Commit**

```bash
git add .cursor/skills/plan-roadmap/SKILL.md
git commit -m "feat: add roadmap planning workflow"
```

---

### Task 6: Validate discovery and roadmap synchronization gates

**Files:**
- Modify only if validation exposes a defect:
  - `.cursor/skills/plan-roadmap/SKILL.md`
  - `.cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md`
  - `.cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md`
  - `.cursor/agents/planner.md`
- Create ignored evidence under: `.agent-delivery/runs/`

**Interfaces:**
- Consumes: Cursor skill and subagent discovery plus the fifteen roadmap dry-run fixtures
- Produces: Evidence that creation, refinement, idempotency, and conflict gates behave correctly

Steps 1 through 4 and Step 8 require an interactive Cursor session, so they remain unchecked user acceptance items. Steps 5 through 7 were completed by static validation and deterministic scenario tracing recorded under `.agent-delivery/runs/roadmap-static-validation/`.

- [ ] **Step 1: Verify discovery** (user acceptance)

Open a fresh Cursor Agent chat. Confirm the skill picker contains `plan-roadmap` and the available subagents contain `planner`.

Expected: both are project-discovered.

Also confirm in the Cursor UI that the discovered `planner` subagent is actually restricted to read-only tools. `readonly: true` in a prompt asset is a declaration, not an enforcement boundary, so its effect must be observed in the product rather than inferred from frontmatter.

- [ ] **Step 2: Verify malformed invocation fails closed** (user acceptance)

Invoke:

```text
/plan-roadmap DRY-RUN
/plan-roadmap m1
/plan-roadmap M1-D1
/plan-roadmap M999
/plan-roadmap DRY-RUN not-a-scenario
```

Expected: the bare `DRY-RUN` and both malformed milestone arguments show the three accepted forms and stop; `M999` reports the requested identifier and the parsed approved milestone identifiers and stops; the unknown scenario lists every valid scenario name and stops. No external mutation occurs in any case.

- [ ] **Step 3: Validate creation and idempotency** (user acceptance)

Invoke:

```text
/plan-roadmap DRY-RUN empty-milestone
/plan-roadmap DRY-RUN idempotent-rerun
/plan-roadmap DRY-RUN refine-draft
```

Expected:

- empty milestone proposes one parent and two child creations;
- idempotent rerun creates and refines nothing; and
- draft refinement preserves sync key and state.

- [ ] **Step 4: Validate fail-closed reconciliation** (user acceptance)

Invoke:

```text
/plan-roadmap DRY-RUN active-ticket-conflict
/plan-roadmap DRY-RUN duplicate-sync-key
/plan-roadmap DRY-RUN duplicate-roadmap-key
/plan-roadmap DRY-RUN malformed-declaration
/plan-roadmap DRY-RUN prefix-collision-key
/plan-roadmap DRY-RUN missing-roadmap-id
/plan-roadmap DRY-RUN milestone-dependency
/plan-roadmap DRY-RUN stale-draft
/plan-roadmap DRY-RUN complete-milestone
/plan-roadmap DRY-RUN authority-divergence
/plan-roadmap DRY-RUN link-pr-unavailable
/plan-roadmap DRY-RUN link-pr-intent-deletion
```

Expected:

- active work is skipped and reported;
- duplicate Linear keys block mutation;
- duplicate approved roadmap keys block even a milestone-scoped run;
- malformed declaration candidates block while headings and prose mentions such as `### Deliverables for M1` do not;
- prefix neighbours such as `M10` and `M1-D10` never satisfy `M1` and `M1-D1`;
- missing roadmap IDs block all writes;
- dependencies are represented without promotion, and an unproven relation schema blocks the edge;
- stale drafts are reported globally but not deleted or canceled;
- a complete milestone produces no fresh drafts;
- `origin/main` divergence or fetch failure blocks before any read of approved intent or Linear mutation;
- an unavailable forge keeps the roadmap-link branch local, never commits to `main`, and reports the exact setup action; and
- a roadmap-link diff that deletes roadmap intent discards the branch and returns BLOCKED.

- [x] **Step 5: Inspect ignored evidence**

Run:

```bash
git status --short
git check-ignore -v .agent-delivery/runs
```

Expected: no dry-run evidence appears in Git status, and `.gitignore` is the matching rule.

- [x] **Step 6: Fix validation defects and rerun affected scenarios**

Change only the smallest prompt or schema responsible for each defect. Rerun the scenario that exposed it. Never weaken a mutation boundary.

- [x] **Step 7: Commit validation fixes if any**

If files changed:

```bash
git add .cursor/skills/plan-roadmap .cursor/agents/planner.md
git commit -m "fix: enforce roadmap planning boundaries"
```

If no files changed, do not create an empty commit.

- [ ] **Step 8: Confirm no external write occurred during acceptance** (user acceptance)

After running the interactive steps, confirm that no Linear issue was created or changed, no branch was pushed, and no pull request was opened by any dry run.

---

### Task 8: Lock plan examples and hardened behavior in place

**Files:**
- Verify: `.gitignore`
- Verify: `.cursor/agents/planner.md`
- Verify: `.cursor/skills/plan-roadmap/SKILL.md`
- Verify: `.cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md`
- Verify: `.cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md`
- Verify: `docs/superpowers/plans/2026-08-25-roadmap-planning-skill.md`
- Verify: `docs/superpowers/specs/2026-08-25-agent-delivery-workflow-design.md`

**Interfaces:**
- Consumes: The shipped workflow assets and this plan's exact file blocks
- Produces: Proof that rerunning this plan cannot revert a hardened safety gate

- [x] **Step 1: Prove the plan's exact blocks match the shipped files**

Run:

```bash
python3 - <<'PY'
import re
from pathlib import Path

plan = Path(
    "docs/superpowers/plans/2026-08-25-roadmap-planning-skill.md"
).read_text()

blocks = re.findall(
    r"^Create `([^`]+)`:\n\n```(?:markdown|gitignore)\n([\s\S]*?)^```$",
    plan,
    re.MULTILINE,
)
assert blocks, "no exact file blocks found in the plan"

checked = []
for target, body in blocks:
    shipped = Path(target).read_text()
    assert body == shipped, target
    checked.append(target)

for required in (
    ".gitignore",
    ".cursor/agents/planner.md",
    ".cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md",
    ".cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md",
    ".cursor/skills/plan-roadmap/SKILL.md",
):
    assert required in checked, required

print(f"plan/implementation parity: OK ({len(checked)} files)")
PY
```

Expected: `plan/implementation parity: OK (5 files)`.

- [x] **Step 2: Prove the approved design records the hardened contract**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

design = Path(
    "docs/superpowers/specs/2026-08-25-agent-delivery-workflow-design.md"
).read_text()

for value in (
    "DRY-RUN-SCENARIOS.md",
    "local-main-bootstrap",
    "origin-main",
    "mechanical roadmap-link pull request",
    "derived from the Linear ticket references",
    "full-value equality",
    "not an enforcement boundary",
    "Stale detection is always global.",
    "malformed declaration detectors",
    "### Deliverables for M1",
    "deletion of roadmap intent",
):
    assert value in design, value

print("design hardening: OK")
PY
```

Expected: `design hardening: OK`.

- [x] **Step 3: Prove the parsing patterns behave as documented**

Run the exact-key, authoring-form, and activity assertions recorded in
`.agent-delivery/runs/roadmap-final-fix/` against the patterns published in
`MILESTONE-TEMPLATES.md`.

Expected: prefix neighbours never match, bullet-prefixed team keys parse, indented and
alternate-dash roadmap identifiers parse, duplicate roadmap keys are detected, milestone
activity derives correctly, unknown scenario names are rejected against the published
valid-name list, malformed and nonexistent milestone arguments are rejected, generated
report paths are unique, and the link-PR fallback path never targets `main` directly.

- [x] **Step 4: Commit**

```bash
git add .gitignore .cursor docs/superpowers
git commit -m "fix: harden roadmap authority and sync-key exactness"
```

---

### Task 7: Prepare first live roadmap synchronization

**Files:**
- Verify: `AGENTS.md`
- Verify: `docs/PRODUCT.md`
- Verify: `docs/TECH.md`
- Verify: `docs/DESIGN.md`
- Verify: `docs/ROADMAP.md`
- Verify: `docs/STRUCTURE.md`
- Verify: `docs/adr/`

**Interfaces:**
- Consumes: Human-approved steering merged to `main`, configured Linear access, and valid roadmap sync IDs
- Produces: A binary readiness decision for the first live `/plan-roadmap` run

Steps 1, 2, and 4 were executed and recorded under `.agent-delivery/runs/roadmap-readiness/`. Every line of the readiness decision is currently `BLOCKED` because no steering exists on `main` yet and the Linear integration reported `needsAuth`. Step 3 remains an unchecked user acceptance item.

- [x] **Step 0: Resolve roadmap authority**

Run:

```bash
python3 - <<'PY'
import subprocess

remotes = subprocess.check_output(["git", "remote"], text=True).split()

if "origin" in remotes:
    mode = "origin-main"
    subprocess.run(["git", "fetch", "origin", "main"], check=True)
    local = subprocess.check_output(
        ["git", "rev-parse", "main"], text=True
    ).strip()
    remote = subprocess.check_output(
        ["git", "rev-parse", "origin/main"], text=True
    ).strip()
    assert local == remote, (
        "BLOCKED: local main "
        f"{local} does not equal origin/main {remote}"
    )
    sha = remote
else:
    mode = "local-main-bootstrap"
    sha = subprocess.check_output(
        ["git", "rev-parse", "main"], text=True
    ).strip()

print(f"roadmap authority: OK mode={mode} sha={sha}")
PY
```

Expected: `roadmap authority: OK mode=local-main-bootstrap sha=<sha>` while no `origin` remote exists, and `mode=origin-main` afterwards. A failed fetch or any divergence is BLOCKED and stops the assessment.

- [x] **Step 1: Verify approved steering exists at the authority commit**

Run:

```bash
python3 - <<'PY'
import re
import subprocess

required = (
    "AGENTS.md",
    "docs/PRODUCT.md",
    "docs/TECH.md",
    "docs/DESIGN.md",
    "docs/ROADMAP.md",
    "docs/STRUCTURE.md",
)

for path in required:
    subprocess.run(["git", "cat-file", "-e", f"main:{path}"], check=True)

agents = subprocess.check_output(
    ["git", "show", "main:AGENTS.md"],
    text=True,
)
delivery = re.search(
    r"^## Delivery Workflow[ \t]*$([\s\S]*?)(?=^## |\Z)",
    agents,
    re.MULTILINE,
)
assert delivery, "AGENTS.md missing ## Delivery Workflow"
team_keys = re.findall(
    r"^[ \t]*(?:[-*+][ \t]+)?Linear team:[ \t]*([^\s<>]+)[ \t]*$",
    delivery.group(1),
    re.MULTILINE,
)
assert len(team_keys) == 1, (
    "## Delivery Workflow must contain exactly one "
    "Linear team: <team-key>"
)

print(f"approved steering on main: OK team={team_keys[0]}")
PY
```

Expected after separate product-steering work: `approved steering on main: OK team=<team-key>`. A missing, malformed, or duplicate `Linear team: <team-key>` entry is BLOCKED. The pattern accepts an optional Markdown bullet prefix, matching the authoring forms in `MILESTONE-TEMPLATES.md`.

- [x] **Step 2: Validate roadmap identifiers**

Run:

```bash
python3 - <<'PY'
import re
import subprocess

roadmap = subprocess.check_output(
    ["git", "show", "main:docs/ROADMAP.md"],
    text=True,
)

MILESTONE = re.compile(r"^[ \t]*##[ \t]+(M\d+)[ \t]+[—–-][ \t]+(\S.*)$")
DELIVERABLE = re.compile(r"^[ \t]*[-*+][ \t]+\[(M\d+-D\d+)\][ \t]+(\S.*)$")

milestones = []
deliverables = []
malformed = []

for number, line in enumerate(roadmap.splitlines(), start=1):
    milestone = MILESTONE.match(line)
    deliverable = DELIVERABLE.match(line)
    if milestone:
        milestones.append(milestone.group(1))
        continue
    if deliverable:
        deliverables.append(deliverable.group(1))
        continue
    if re.match(r"^[ \t]*##[ \t]*.*\bM\d+\b", line):
        malformed.append((number, line))
    elif re.search(r"\[M\d+-D\d+\]", line):
        malformed.append((number, line))

assert not malformed, f"malformed identifier lines: {malformed}"
assert milestones, "no stable milestone IDs"
assert deliverables, "no stable deliverable IDs"
assert len(milestones) == len(set(milestones)), "duplicate milestone IDs"
assert len(deliverables) == len(set(deliverables)), "duplicate deliverable IDs"

print(
    "roadmap identifiers: OK "
    f"milestones={len(milestones)} deliverables={len(deliverables)}"
)
PY
```

Expected: `roadmap identifiers: OK milestones=<n> deliverables=<n>`. A line that advertises an identifier but fails its published pattern is reported rather than silently skipped, and duplicate identifiers are BLOCKED.

- [ ] **Step 3: Verify Linear access without mutation** (user acceptance)

Using the configured Linear integration:

1. Read the target team.
2. List workflow states.
3. Search issue descriptions for `Roadmap sync key:`, then filter results by exact parsed key.
4. Confirm issue creation, update, parent-link, and dependency-link tools are available, and record the exact current schema for each relation operation.

Expected: read access succeeds; `Draft` or `Needs Planning` exists; required mutation tools are available. Do not write during this check.

- [x] **Step 4: Report readiness**

Produce:

```text
Roadmap authority: READY or BLOCKED
Approved steering on main: READY or BLOCKED
Linear team configuration: READY or BLOCKED
Roadmap stable IDs: READY or BLOCKED
Linear read access: READY or BLOCKED
Linear draft mutation tools: READY or BLOCKED
Roadmap link pull request path: READY or BLOCKED
First roadmap sync: READY or BLOCKED
```

Do not run a live synchronization until every line is `READY`.
