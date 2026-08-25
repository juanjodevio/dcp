# Roadmap Planning Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a project-local `/plan-roadmap` skill that turns the approved roadmap into dependency-ordered milestones and idempotently creates or refines draft Linear tickets.

**Architecture:** The version of `docs/ROADMAP.md` merged into `main` is the authorization boundary. A read-only Planner subagent produces structured milestone plans; the parent skill applies only permitted draft mutations through Linear and writes an audit report locally. Stable roadmap sync keys prevent duplicate tickets and support reconciliation.

**Tech Stack:** Cursor Agent Skills, Cursor custom subagents, Markdown/YAML frontmatter, Linear MCP, Git

## Global Constraints

- Run locally and only when explicitly invoked as `/plan-roadmap` or `/plan-roadmap MILESTONE-ID`.
- Read the approved roadmap from `main`, not from unmerged workspace edits.
- Approved roadmap content authorizes creation and refinement of corresponding draft work without another planning approval.
- Create or refine Linear tickets only in `Draft` or `Needs Planning`.
- Never move work to `Agent Ready`.
- Never mutate active, completed, canceled, or otherwise non-draft tickets.
- Never delete, cancel, close, or merge tickets.
- Never edit `ROADMAP.md`, product steering documents, ADRs, or application code.
- Planner model remains configurable by inheriting the parent model.
- Planner runs are fresh and read-only.
- Use stable roadmap sync keys to make reruns idempotent.
- Conflicts, duplicate sync keys, ambiguous roadmap intent, or unsupported Linear mutations fail closed.
- Linear owns ticket state; the approved roadmap owns milestone intent.
- Do not require Cursor Cloud, a service, PostgreSQL, webhooks, or a credential broker.

---

### Task 1: Establish local workflow hygiene

**Files:**
- Create: `.gitignore`

**Interfaces:**
- Consumes: Local visual-companion and workflow state directories
- Produces: Repository-wide ignore rules shared by roadmap planning and ticket delivery

- [ ] **Step 1: Verify the state directories are currently unignored**

Run:

```bash
git check-ignore .superpowers .agent-delivery
```

Expected: exit code `1` with no output.

- [ ] **Step 2: Create the ignore rules**

Create `.gitignore`:

```gitignore
.superpowers/
.agent-delivery/
```

- [ ] **Step 3: Verify both directories are ignored**

Run:

```bash
mkdir -p .agent-delivery/runs && git check-ignore -v .superpowers .agent-delivery/runs
```

Expected: both paths are attributed to `.gitignore`.

- [ ] **Step 4: Commit**

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
- Produces: A Roadmap Coverage Report, Milestone Plan, Reconciliation Report, or ticket-level Planner Report

- [ ] **Step 1: Create the Planner**

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
- identify missing, duplicate, stale, conflicting, or uncovered Linear work.

For ticket refinement:
- decide whether the supplied ticket is atomic;
- propose bounded children, dependencies, contracts, integration work, acceptance criteria, verification commands, risks, and steering references.

Do not edit files, call mutating tools, implement code, change roadmap intent, approve your own plan, or invent missing product intent. The parent workflow owns permitted Linear mutations. Return only the report schema supplied by the caller. Mark ambiguity as BLOCKED.
```

- [ ] **Step 2: Validate the Planner configuration**

Run:

```bash
python - <<'PY'
from pathlib import Path

text = Path(".cursor/agents/planner.md").read_text()
assert text.startswith("---\n")
assert "name: planner\n" in text
assert "model: inherit\n" in text
assert "readonly: true\n" in text
assert "stable roadmap sync key" in text
assert "parent workflow owns permitted Linear mutations" in text

print("planner agent: OK")
PY
```

Expected: `planner agent: OK`.

- [ ] **Step 3: Commit**

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

- [ ] **Step 1: Create milestone templates**

Create `.cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md`:

```markdown
# Roadmap Planning Templates

Use every heading. Write `None` when a non-verdict section has no entries.

## Stable identifiers

Roadmap milestone headings use:

`## M<number> — milestone name`

Roadmap deliverables use:

`- [M<number>-D<number>] deliverable outcome`

Every synced Linear issue description contains:

`Roadmap sync key: M<number>` for a milestone parent.

`Roadmap sync key: M<number>-D<number>` for a deliverable.

Sync keys are immutable. A renamed outcome keeps its existing key.

## Roadmap Coverage Report

### Approved roadmap SHA
### Milestones inspected
### Covered deliverables
### Missing deliverables
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
Include roadmap outcome, completion evidence, risks, and `Roadmap sync key: M<number>`.
### State
Use `Draft` or `Needs Planning`.

## Linear Deliverable Ticket

### Title
### Description
Include outcome, acceptance criteria, verification, contracts, risks, dependencies, and `Roadmap sync key: M<number>-D<number>`.
### Parent sync key
### Dependency sync keys
### State
Use `Draft` or `Needs Planning`.

## Reconciliation Report

### Approved roadmap SHA
### Created tickets
### Refined tickets
### Unchanged tickets
### Skipped active tickets
### Duplicate conflicts
### Unsupported mutations
### Remaining coverage gaps
### Result
Use `SYNCED`, `PARTIAL`, or `BLOCKED`.
```

- [ ] **Step 2: Validate stable-key and verdict vocabulary**

Run:

```bash
python - <<'PY'
from pathlib import Path

text = Path(".cursor/skills/plan-roadmap/MILESTONE-TEMPLATES.md").read_text()
for value in (
    "Roadmap sync key:",
    "READY_TO_SYNC",
    "SYNCED",
    "PARTIAL",
    "BLOCKED",
    "Skipped active tickets",
):
    assert value in text, value

print("milestone templates: OK")
PY
```

Expected: `milestone templates: OK`.

- [ ] **Step 3: Commit**

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

- [ ] **Step 1: Create dry-run scenarios**

Create `.cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md`:

```markdown
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
```

- [ ] **Step 2: Validate scenario coverage**

Run:

```bash
python - <<'PY'
from pathlib import Path

text = Path(".cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md").read_text()
names = (
    "empty-milestone",
    "idempotent-rerun",
    "refine-draft",
    "active-ticket-conflict",
    "duplicate-sync-key",
    "missing-roadmap-id",
    "milestone-dependency",
    "stale-draft",
)
for name in names:
    assert f"## {name}\n" in text, name
assert text.count("## ") == 8

print("roadmap dry-run scenarios: OK")
PY
```

Expected: `roadmap dry-run scenarios: OK`.

- [ ] **Step 3: Commit**

```bash
git add .cursor/skills/plan-roadmap/DRY-RUN-SCENARIOS.md
git commit -m "test: add roadmap planning scenarios"
```

---

### Task 5: Implement the explicit plan-roadmap skill

**Files:**
- Create: `.cursor/skills/plan-roadmap/SKILL.md`

**Interfaces:**
- Consumes: `/plan-roadmap`, `/plan-roadmap MILESTONE-ID`, or `/plan-roadmap DRY-RUN scenario-name`; approved roadmap from `main`; steering documents; Linear MCP; Planner; milestone templates
- Produces: Idempotent draft Linear milestone parents and deliverable tickets plus a reconciliation report

- [ ] **Step 1: Create the skill**

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
```

- [ ] **Step 2: Validate skill metadata and safety boundaries**

Run:

```bash
python - <<'PY'
from pathlib import Path

path = Path(".cursor/skills/plan-roadmap/SKILL.md")
text = path.read_text()

assert text.startswith("---\n")
assert "name: plan-roadmap\n" in text
assert "disable-model-invocation: true\n" in text
assert "/plan-roadmap MILESTONE-ID" in text
assert "Read `docs/ROADMAP.md` from `main`" in text
assert "Do not move any issue to Agent Ready." in text
assert "Never delete, cancel, close, or downgrade work." in text
assert len(text.splitlines()) < 500

for reference in ("MILESTONE-TEMPLATES.md", "DRY-RUN-SCENARIOS.md"):
    assert reference in text
    assert path.with_name(reference).is_file()

print("plan-roadmap skill: OK")
PY
```

Expected: `plan-roadmap skill: OK`.

- [ ] **Step 3: Scan skill and Planner for unfinished language**

Run:

```bash
python - <<'PY'
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

- [ ] **Step 4: Commit**

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
- Consumes: Cursor skill and subagent discovery plus eight roadmap dry-run fixtures
- Produces: Evidence that creation, refinement, idempotency, and conflict gates behave correctly

- [ ] **Step 1: Verify discovery**

Open a fresh Cursor Agent chat. Confirm the skill picker contains `plan-roadmap` and the available subagents contain `planner`.

Expected: both are project-discovered.

- [ ] **Step 2: Verify malformed invocation fails closed**

Invoke:

```text
/plan-roadmap DRY-RUN
```

Expected: usage shows the three accepted forms and no external mutation occurs.

- [ ] **Step 3: Validate creation and idempotency**

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

- [ ] **Step 4: Validate fail-closed reconciliation**

Invoke:

```text
/plan-roadmap DRY-RUN active-ticket-conflict
/plan-roadmap DRY-RUN duplicate-sync-key
/plan-roadmap DRY-RUN missing-roadmap-id
/plan-roadmap DRY-RUN milestone-dependency
/plan-roadmap DRY-RUN stale-draft
```

Expected:

- active work is skipped and reported;
- duplicate keys block mutation;
- missing roadmap IDs block all writes;
- dependencies are represented without promotion; and
- stale drafts are reported but not deleted or canceled.

- [ ] **Step 5: Inspect ignored evidence**

Run:

```bash
git status --short
git check-ignore -v .agent-delivery/runs
```

Expected: no dry-run evidence appears in Git status, and `.gitignore` is the matching rule.

- [ ] **Step 6: Fix validation defects and rerun affected scenarios**

Change only the smallest prompt or schema responsible for each defect. Rerun the scenario that exposed it. Never weaken a mutation boundary.

- [ ] **Step 7: Commit validation fixes if any**

If files changed:

```bash
git add .cursor/skills/plan-roadmap .cursor/agents/planner.md
git commit -m "fix: enforce roadmap planning boundaries"
```

If no files changed, do not create an empty commit.

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

- [ ] **Step 1: Verify approved steering exists on main**

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
    r"^## Delivery Workflow\s*$([\s\S]*?)(?=^## |\Z)",
    agents,
    re.MULTILINE,
)
assert delivery, "AGENTS.md missing ## Delivery Workflow"
team_keys = re.findall(
    r"^Linear team: ([^\s<>]+)\s*$",
    delivery.group(1),
    re.MULTILINE,
)
assert len(team_keys) == 1, (
    "## Delivery Workflow must contain exactly one "
    "Linear team: <team-key>"
)

print("approved steering on main: OK")
PY
```

Expected after separate product-steering work: `approved steering on main: OK`. A missing, malformed, or duplicate `Linear team: <team-key>` entry is BLOCKED.

- [ ] **Step 2: Validate roadmap identifiers**

Run:

```bash
python3 - <<'PY'
import re
import subprocess

roadmap = subprocess.check_output(
    ["git", "show", "main:docs/ROADMAP.md"],
    text=True,
)

milestones = re.findall(r"^## (M\d+) — .+$", roadmap, re.MULTILINE)
deliverables = re.findall(r"^- \[(M\d+-D\d+)\] .+$", roadmap, re.MULTILINE)

assert milestones, "no stable milestone IDs"
assert deliverables, "no stable deliverable IDs"
assert len(milestones) == len(set(milestones)), "duplicate milestone IDs"
assert len(deliverables) == len(set(deliverables)), "duplicate deliverable IDs"

print("roadmap identifiers: OK")
PY
```

Expected: `roadmap identifiers: OK`.

- [ ] **Step 3: Verify Linear access without mutation**

Using the configured Linear integration:

1. Read the target team.
2. List workflow states.
3. Search issue descriptions for `Roadmap sync key:`.
4. Confirm issue creation, update, parent-link, and dependency-link tools are available.

Expected: read access succeeds; `Draft` or `Needs Planning` exists; required mutation tools are available. Do not write during this check.

- [ ] **Step 4: Report readiness**

Produce:

```text
Approved steering on main: READY or BLOCKED
Linear team configuration: READY or BLOCKED
Roadmap stable IDs: READY or BLOCKED
Linear read access: READY or BLOCKED
Linear draft mutation tools: READY or BLOCKED
First roadmap sync: READY or BLOCKED
```

Do not run a live synchronization until every line is `READY`.
