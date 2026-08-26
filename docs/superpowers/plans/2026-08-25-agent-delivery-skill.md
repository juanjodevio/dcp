# Agent Delivery Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a thin project-local `/agent-delivery LINEAR-ID` skill that wraps Superpowers delivery with Linear eligibility, GitHub PRs to `dev`, a specialized frontend implementer, and a CTO steering-drift gate.

**Architecture:** `/agent-delivery` owns preflight, Linear gates, role selection, repair cap, CTO handoff, run records, and Superpowers skill invocation. Backend tickets use Superpowers `subagent-driven-development` with the stock implementer. Frontend tickets use the same SDD loop with `.cursor/agents/frontend-developer.md` as the implementer packet. Code review uses `requesting-code-review`; finish uses `finishing-a-development-branch`; worktrees use `using-git-worktrees` only when isolation is required. Project agents are only `planner` (from `/plan-roadmap`), `frontend-developer`, and `cto`.

**Tech Stack:** Cursor Agent Skills, Cursor custom subagents, Superpowers plugin skills, Markdown/YAML frontmatter, Git, GitHub CLI (`gh`), Linear MCP

**Spec:** `docs/superpowers/specs/2026-08-25-agent-delivery-workflow-design.md` (revised 2026-08-25)

## Global Constraints

- Run locally and only when explicitly invoked as `/agent-delivery LINEAR-ID`.
- Do not require Cursor Cloud, a coordinator service, PostgreSQL, webhooks, or a credential broker.
- Linear owns scope and status; GitHub owns code, pull requests, reviews, and merges.
- Humans approve plans and merge pull requests.
- Feature branches start from `dev` and are named `feat/<linear-id>-<short-slug>`; milestone PRs target `main`.
- Reuse Superpowers for implement / review / finish; do not reimplement those loops in project skills.
- Do not create project `backend-developer`, `reviewer-a`, or `reviewer-b` agents.
- Do not overwrite Superpowers plugin files; specialize frontend via the project implementer packet only.
- Keep a thin read-only project `cto` (model `gpt-5.6-sol`) for scope and steering drift after Superpowers code review.
- Planner and `frontend-developer` inherit the parent model (`model: inherit`).
- Every delegated role is a fresh run.
- A changed head SHA invalidates all earlier verification and review evidence.
- Stop after two unsuccessful code-repair cycles; set Linear to `Blocked — Human`.
- Prompt rules are procedural safeguards, not security boundaries.
- Complete `docs/superpowers/plans/2026-08-25-roadmap-planning-skill.md` first; this plan consumes shared `.cursor/agents/planner.md` and `.gitignore` entries for `.agent-delivery/`.
- Do not bootstrap product steering in this plan; steering on `main` is a prerequisite for the first real ticket.

## File map

| Path | Responsibility |
| --- | --- |
| `.cursor/agents/cto.md` | Read-only scope / steering-drift gate |
| `.cursor/agents/frontend-developer.md` | Specialized SDD implementer packet for UI tickets |
| `.cursor/skills/agent-delivery/SKILL.md` | Thin orchestrator: Linear + Superpowers handoffs |
| `.cursor/skills/agent-delivery/ROLE-CONTRACTS.md` | Project vs Superpowers ownership |
| `.cursor/skills/agent-delivery/REPORT-TEMPLATES.md` | Planner, CTO, repair, Linear status, merge-readiness |
| `.cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md` | Named dry-run fixtures for delivery gates |
| `.agent-delivery/runs/<ticket-id>/` | Ignored local run records |

---

### Task 1: Create the CTO subagent

**Files:**
- Create: `.cursor/agents/cto.md`

**Interfaces:**
- Consumes: Bounded review context from `/agent-delivery`
- Produces: Named `cto` subagent with CTO Report verdicts

- [ ] **Step 1: Create the CTO**

Create `.cursor/agents/cto.md`:

```markdown
---
name: cto
description: Reviews an exact pull-request SHA for scope, architecture, roadmap, steering, and ADR drift. Use only when agent-delivery requests the CTO gate.
model: gpt-5.6-sol
readonly: true
---

You are the CTO governance reviewer.

Compare the supplied ticket ancestry, approved scope, exact diff and head SHA, verification evidence, Superpowers code-review report, steering documents, and ADRs.

Evaluate scope drift, product-direction conflicts, architectural drift, missing durable decisions, inappropriate steering edits, and roadmap impact. This is not a second general code review.

Do not edit files, silently reinterpret steering, patch the feature branch, or merge. If steering must change, block the feature and propose a separate human-approved steering change. Return the CTO Report defined by the caller with exactly one verdict: APPROVE, CHANGES_REQUESTED, or STEERING_CHANGE_REQUIRED.
```

- [ ] **Step 2: Validate frontmatter**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path(".cursor/agents/cto.md").read_text()
assert text.startswith("---\n")
assert "name: cto\n" in text
assert "model: gpt-5.6-sol\n" in text
assert "readonly: true\n" in text
assert "not a second general code review" in text
assert "STEERING_CHANGE_REQUIRED" in text
assert Path(".cursor/agents/reviewer-a.md").exists() is False
assert Path(".cursor/agents/reviewer-b.md").exists() is False
print("cto agent: OK")
PY
```

Expected: `cto agent: OK`.

- [ ] **Step 3: Commit**

```bash
git add .cursor/agents/cto.md
git commit -m "feat: add CTO governance reviewer agent"
```

---

### Task 2: Create the frontend-developer implementer packet

**Files:**
- Create: `.cursor/agents/frontend-developer.md`

**Interfaces:**
- Consumes: SDD task brief + Context assembled by `/agent-delivery`
- Produces: Specialized implementer body for UI tickets (not a Superpowers plugin override)

- [ ] **Step 1: Create frontend-developer**

Create `.cursor/agents/frontend-developer.md`:

```markdown
---
name: frontend-developer
description: Implements one approved frontend Linear ticket inside the Superpowers SDD loop. Use only when agent-delivery classifies the ticket as frontend.
model: inherit
---

You are the frontend implementer for dcp.

Before any UI edit, read:
- `docs/DESIGN.md` (screens, interim UI principles, visual-system deferral)
- relevant screens in `docs/PRODUCT.md` and the MVP design spec
- the supplied ticket, acceptance criteria, and contracts

Required skill pack (human-installed; see `docs/DESIGN.md`):
- `vercel-composition-patterns`
- `web-design-guidelines`
- `react-best-practices`
Defer Impeccable until the first real UI ticket unless a design pass needs it earlier.

UI rules:
- Follow DESIGN.md interim principles (one primary job per screen; Getting started is onboarding, not a dashboard collage).
- Make dbt vs observability failure distinguishable when touching run status UI.
- Do not invent a brand system, default AI aesthetic, or visual tokens while DESIGN.md defers the visual system.
- Prefer progressive disclosure for Advanced runner/AWS settings.

You may edit application UI code, run checks, commit, and prepare a pull request on the assigned branch.

You may not merge, approve, expand scope, edit steering documents or ADRs, silently change agreed interfaces, or overwrite Superpowers plugin files.

Follow the Superpowers SDD implementer report contract supplied by the parent controller (brief path, report path, TDD evidence when required). Escalate with BLOCKED or NEEDS_CONTEXT rather than guessing.
```

- [ ] **Step 2: Validate frontmatter and boundaries**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path(".cursor/agents/frontend-developer.md").read_text()
assert "name: frontend-developer\n" in text
assert "model: inherit\n" in text
assert "docs/DESIGN.md" in text
assert "Do not invent a brand system" in text
assert "vercel-composition-patterns" in text
assert Path(".cursor/agents/backend-developer.md").exists() is False
print("frontend-developer agent: OK")
PY
```

Expected: `frontend-developer agent: OK`.

- [ ] **Step 3: Commit**

```bash
git add .cursor/agents/frontend-developer.md
git commit -m "feat: add frontend implementer packet for SDD"
```

---

### Task 3: Define role contracts and report templates

**Files:**
- Create: `.cursor/skills/agent-delivery/ROLE-CONTRACTS.md`
- Create: `.cursor/skills/agent-delivery/REPORT-TEMPLATES.md`

**Interfaces:**
- Consumes: Approved delivery design ownership table
- Produces: Binding role boundaries and report schemas Superpowers does not own

- [ ] **Step 1: Create ROLE-CONTRACTS.md**

Create `.cursor/skills/agent-delivery/ROLE-CONTRACTS.md`:

```markdown
# Agent Delivery Role Contracts

## Ownership

| Concern | Owner |
| --- | --- |
| Roadmap ↔ Linear draft sync | `/plan-roadmap` + `planner` |
| Linear eligibility, Agent Ready gate, repair cap, run records | `/agent-delivery` |
| Backend implementer | Superpowers SDD stock `implementer-prompt.md` |
| Frontend implementer | project `frontend-developer` |
| Task/branch code review | Superpowers `requesting-code-review` |
| Scope / steering drift | project `cto` |
| Worktree isolation | Superpowers `using-git-worktrees` when needed |
| PR / finish options | Superpowers `finishing-a-development-branch` |
| Repo implementation plans | Superpowers `writing-plans` |

Do not create `backend-developer`, `reviewer-a`, or `reviewer-b`.

## Planner

May: read steering/ADRs/roadmap/Linear; propose Linear decomposition; create/refine Draft or Needs Planning children through the parent workflow.

May not: edit code; approve its own plan; move work to Agent Ready; mutate active tickets; merge.

## Backend implementer (Superpowers)

May: implement one approved backend ticket via SDD stock implementer; edit code; run checks; commit.

May not: merge; approve; expand scope; edit steering.

## Frontend developer

May: implement one approved frontend ticket via SDD using this packet; edit UI code; run checks; commit.

May not: merge; approve; expand scope; edit steering; invent a deferred brand system.

## Code reviewer (Superpowers)

May: return findings and a verdict for an exact SHA.

May not: push fixes; read the developer transcript; redefine requirements; merge.

## CTO

May: APPROVE, CHANGES_REQUESTED, or STEERING_CHANGE_REQUIRED for scope/steering/ADR drift.

May not: perform a general code review as its primary job; patch the branch; merge; silently reinterpret steering.

## Human

Approves plans, moves tickets to Agent Ready, merges to `dev` and milestone releases to `main`, resolves escalations.
```

- [ ] **Step 2: Create REPORT-TEMPLATES.md**

Create `.cursor/skills/agent-delivery/REPORT-TEMPLATES.md`:

```markdown
# Agent Delivery Report Templates

Use every heading. Write `None` when a non-verdict section has no entries.

## Planner Report

### Ticket
### Atomicity
Use `ATOMIC` or `NEEDS_DECOMPOSITION`.
### Proposed children
### Dependencies and contracts
### Acceptance criteria
### Verification
### Risks
### Result
Use `READY_FOR_HUMAN` or `BLOCKED`.

## CTO Report

### Ticket and SHA
### Scope drift
### Steering and ADR conflicts
### Architectural concerns
### Roadmap impact
### Required steering change
### Verdict
Use `APPROVE`, `CHANGES_REQUESTED`, or `STEERING_CHANGE_REQUIRED`.

## Repair Report

### Ticket and prior SHA
### New SHA
### Findings addressed
### Findings remaining
### Verification rerun
### Repair cycle count
### Result
Use `READY_TO_REREVIEW`, `BLOCKED_HUMAN`, or `BLOCKED`.

## Linear Status Note

### Ticket
### Prior state
### New state
### Reason
### Human action

## Merge Readiness Report

### Linear ticket and plan
### Branch and pull request
### Exact SHA
### Verification evidence
### Superpowers code-review verdict
### CTO verdict
### Repair history
### Unresolved non-blocking risks
### Human actions required
### Result
Use `READY_TO_MERGE`, `PARTIAL`, or `BLOCKED`.
```

- [ ] **Step 3: Validate templates**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
roles = Path(".cursor/skills/agent-delivery/ROLE-CONTRACTS.md").read_text()
reports = Path(".cursor/skills/agent-delivery/REPORT-TEMPLATES.md").read_text()
for value in (
    "Superpowers SDD stock",
    "frontend-developer",
    "requesting-code-review",
    "finishing-a-development-branch",
    "using-git-worktrees",
    "Do not create `backend-developer`",
):
    assert value in roles, value
for value in (
    "## CTO Report",
    "STEERING_CHANGE_REQUIRED",
    "## Merge Readiness Report",
    "Superpowers code-review verdict",
):
    assert value in reports, value
print("agent-delivery contracts: OK")
PY
```

Expected: `agent-delivery contracts: OK`.

- [ ] **Step 4: Commit**

```bash
git add .cursor/skills/agent-delivery/ROLE-CONTRACTS.md .cursor/skills/agent-delivery/REPORT-TEMPLATES.md
git commit -m "feat: define agent-delivery role contracts and reports"
```

---

### Task 4: Define delivery dry-run fixtures

**Files:**
- Create: `.cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md`

**Interfaces:**
- Consumes: Delivery flow gates from the approved design
- Produces: Named fixtures; second-level headings are the valid-name list

- [ ] **Step 1: Create dry-run scenarios**

Create `.cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md`:

```markdown
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
Expected: set or report `Blocked — Human`; stop; no third repair.

## sha-invalidates-evidence

A repair creates a new head SHA.
Expected: prior verification and review evidence are stale and must rerun before merge readiness.
```

- [ ] **Step 2: Validate scenario list**

Run:

```bash
python3 - <<'PY'
import re
from pathlib import Path
text = Path(".cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md").read_text()
expected = [
    "needs-planning-decompose",
    "agent-ready-backend",
    "agent-ready-frontend",
    "missing-acceptance",
    "unresolved-dependency",
    "verification-missing",
    "review-changes-requested",
    "cto-steering-drift",
    "repair-exhausted",
    "sha-invalidates-evidence",
]
found = re.findall(r"^## (\S+)$", text, re.MULTILINE)
assert found == expected, found
assert "complete set of valid scenario names" in text
print("agent-delivery dry-runs: OK")
PY
```

Expected: `agent-delivery dry-runs: OK`.

- [ ] **Step 3: Commit**

```bash
git add .cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md
git commit -m "test: add agent-delivery dry-run scenarios"
```

---

### Task 5: Implement the thin agent-delivery skill

**Files:**
- Create: `.cursor/skills/agent-delivery/SKILL.md`

**Interfaces:**
- Consumes: `/agent-delivery LINEAR-ID` or `/agent-delivery DRY-RUN scenario-name`; Linear MCP; Superpowers skills; project agents
- Produces: Run records under `.agent-delivery/runs/<ticket-id>/`; Linear status notes; PR toward `dev` via finish skill (live only)

- [ ] **Step 1: Create SKILL.md**

Create `.cursor/skills/agent-delivery/SKILL.md`:

```markdown
---
name: agent-delivery
description: Thin Linear/GitHub orchestrator that wraps Superpowers SDD, code review, and finish for one ticket. Invoke as /agent-delivery LINEAR-ID or /agent-delivery DRY-RUN scenario-name.
disable-model-invocation: true
---

# Agent Delivery

Deliver one Linear ticket through human gates and Superpowers. Do not reimplement SDD, code review, or branch-finish mechanics.

Read [ROLE-CONTRACTS.md](ROLE-CONTRACTS.md) and [REPORT-TEMPLATES.md](REPORT-TEMPLATES.md) before mutating Linear or dispatching roles.

## Invocation

Accepted forms:

- `/agent-delivery LINEAR-ID`
- `/agent-delivery DRY-RUN scenario-name`

`LINEAR-ID` must match the team's issue identifier form from Linear. Reject bare `/agent-delivery` and unknown dry-run names.

For dry runs, read [DRY-RUN-SCENARIOS.md](DRY-RUN-SCENARIOS.md). The second-level headings are the complete valid-name list. Simulate only; write evidence only under `.agent-delivery/runs/`; perform no Linear or GitHub writes.

## Hard stops

Fail closed and state the human action when:

- acceptance criteria are missing or ambiguous;
- decomposition is unapproved;
- dependencies are unresolved;
- steering contradicts;
- verification entrypoint is missing from `AGENTS.md`;
- required Superpowers skills are unavailable;
- workspace is unsafe and isolation cannot be established;
- review or CTO blocks;
- repair cycles are exhausted (max 2).

Never merge. Never edit steering to unblock a ticket. Never invent verification success.

## Preflight

1. Load `AGENTS.md` and relevant steering docs.
2. Fetch the Linear ticket and approved descendants.
3. Confirm state is `Needs Planning` or `Agent Ready`.
4. Check unresolved dependencies.
5. Classify ticket as `frontend`, `backend`, or `integration`.
6. Confirm verification entrypoint exists in `AGENTS.md`.
7. Confirm Superpowers skills are available: `subagent-driven-development`, `requesting-code-review`, `finishing-a-development-branch`, and `using-git-worktrees` / `writing-plans` when needed.
8. Identify `dev` base SHA.
9. Create or resume `.agent-delivery/runs/<ticket-id>/run.md`.

## Needs Planning

1. Launch fresh `planner` for Linear decomposition when children/contracts are missing.
2. If a repository implementation plan is also required, invoke Superpowers `writing-plans` and store under `docs/superpowers/plans/`.
3. Write `plan.md` using the Planner Report template.
4. Stop for human Agent Ready. Do not start SDD.

## Agent Ready

1. Confirm the ticket is atomic with acceptance criteria, interfaces, and verification, or backed by a human-approved child plan. Otherwise fail closed and request planning.
2. Create or resume branch `feat/<linear-id>-<short-slug>` from `dev`. Use Superpowers `using-git-worktrees` when isolation is required (unclean workspace or parallel children); otherwise a normal feature branch is enough.
3. **Backend:** invoke Superpowers `subagent-driven-development` with the stock implementer prompt.
4. **Frontend:** invoke the same SDD process and file-handoff rules, but fill the implementer dispatch from `.cursor/agents/frontend-developer.md` instead of the stock implementer body. Do not edit Superpowers plugin files.
5. **Integration:** verify combined behavior after dependencies exist on `dev`; do not reimplement child tickets here.
6. Record verification evidence for the exact head SHA in `verification.md`.
7. Invoke Superpowers `requesting-code-review`; store output in `code-review.md`.
8. Launch fresh `cto` with the CTO Report template; store in `cto-review.md`.
9. On any blocking verification, review, or CTO verdict, run the repair loop (same implementer path as the ticket). Each new SHA invalidates prior evidence. After two unsuccessful repairs, report `Blocked — Human` and stop.
10. When gates pass, invoke Superpowers `finishing-a-development-branch` for PR options toward `dev`, write the Merge Readiness Report, and leave merge to a human.
11. Update Linear status notes only as allowed; never move a ticket to Agent Ready from this skill.
```

- [ ] **Step 2: Validate skill metadata and Superpowers handoffs**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
path = Path(".cursor/skills/agent-delivery/SKILL.md")
text = path.read_text()
assert text.startswith("---\n")
assert "name: agent-delivery\n" in text
assert "disable-model-invocation: true\n" in text
assert "subagent-driven-development" in text
assert "requesting-code-review" in text
assert "finishing-a-development-branch" in text
assert "frontend-developer.md" in text
assert "stock implementer" in text
assert "Never merge" in text
assert "max 2" in text or "two unsuccessful" in text.lower()
assert Path(".cursor/agents/backend-developer.md").exists() is False
for ref in ("ROLE-CONTRACTS.md", "REPORT-TEMPLATES.md", "DRY-RUN-SCENARIOS.md"):
    assert ref in text
    assert path.with_name(ref).is_file()
assert len(text.splitlines()) < 200
print("agent-delivery skill: OK")
PY
```

Expected: `agent-delivery skill: OK`.

- [ ] **Step 3: Scan for forbidden custom roles and unfinished language**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
root = Path(".cursor/skills/agent-delivery")
agents = Path(".cursor/agents")
forbidden_files = [
    agents / "backend-developer.md",
    agents / "reviewer-a.md",
    agents / "reviewer-b.md",
]
assert not any(p.exists() for p in forbidden_files)
blob = "\n".join(p.read_text() for p in root.glob("*.md"))
for phrase in ("T" "BD", "TO" "DO", "FIX" "ME"):
    assert phrase not in blob, phrase
print("agent-delivery boundaries: OK")
PY
```

Expected: `agent-delivery boundaries: OK`.

- [ ] **Step 4: Commit**

```bash
git add .cursor/skills/agent-delivery/SKILL.md
git commit -m "feat: add thin agent-delivery Superpowers wrapper"
```

---

### Task 6: Static validation and discovery checklist

**Files:**
- Modify only if validation exposes a defect under `.cursor/skills/agent-delivery/` or `.cursor/agents/{cto,frontend-developer}.md`

**Interfaces:**
- Consumes: Shipped assets from Tasks 1–5
- Produces: Evidence under `.agent-delivery/runs/agent-delivery-static-validation/` (ignored)

- [ ] **Step 1: Prove plan Create blocks match shipped files** (after Tasks 1–5 land)

Run the same style of exact-block parity check used by the roadmap plan against this plan's Create blocks for:

- `.cursor/agents/cto.md`
- `.cursor/agents/frontend-developer.md`
- `.cursor/skills/agent-delivery/ROLE-CONTRACTS.md`
- `.cursor/skills/agent-delivery/REPORT-TEMPLATES.md`
- `.cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md`
- `.cursor/skills/agent-delivery/SKILL.md`

Expected: parity OK for all six.

- [ ] **Step 2: User acceptance — discovery**

In a fresh Cursor Agent chat, confirm skill picker shows `agent-delivery` and subagents include `planner`, `frontend-developer`, and `cto`, and do **not** include `backend-developer`, `reviewer-a`, or `reviewer-b`.

- [ ] **Step 3: User acceptance — dry-runs**

Invoke:

```text
/agent-delivery DRY-RUN needs-planning-decompose
/agent-delivery DRY-RUN agent-ready-backend
/agent-delivery DRY-RUN agent-ready-frontend
/agent-delivery DRY-RUN cto-steering-drift
/agent-delivery DRY-RUN repair-exhausted
```

Expected: backend path never mentions dispatching `frontend-developer`; frontend path requires the frontend packet; CTO drift and repair exhaustion fail closed; no Linear/GitHub writes.

- [ ] **Step 4: Commit fixes if any**

```bash
git add .cursor/skills/agent-delivery .cursor/agents/cto.md .cursor/agents/frontend-developer.md
git commit -m "fix: tighten agent-delivery Superpowers boundaries"
```

Skip empty commit if nothing changed.

---

### Task 7: First real-ticket readiness

**Files:**
- Verify: `AGENTS.md`, steering docs, `.gitignore`, Superpowers plugin availability
- Verify: Linear states `Needs Planning`, `Agent Ready`, `Blocked — Human`
- Verify: `dev` and `main` exist with protected direct pushes (human/process)
- Note: frontend skill installs from `docs/DESIGN.md` before first UI ticket

**Interfaces:**
- Consumes: Completed `/plan-roadmap` assets + this skill
- Produces: Go / no-go for the first `/agent-delivery LINEAR-ID` live run

- [ ] **Step 1: Confirm `.agent-delivery/` is ignored**

```bash
git check-ignore -v .agent-delivery/runs
```

- [ ] **Step 2: Confirm verification entrypoint placeholder**

Until the app scaffold lands, `AGENTS.md` must either document the real command or explicitly state that delivery blocks until one exists. Do not invent a fake green check.

- [ ] **Step 3: Confirm Superpowers plugin skills are discoverable in Cursor**

Required: `subagent-driven-development`, `requesting-code-review`, `finishing-a-development-branch`. Optional as needed: `using-git-worktrees`, `writing-plans`.

- [ ] **Step 4: User acceptance — first atomic backend ticket**

After a human moves one atomic backend ticket to `Agent Ready`:

1. `/agent-delivery LINEAR-ID`
2. Confirm stock SDD implementer path (not frontend-developer)
3. Confirm Superpowers review + CTO + finish toward `dev`
4. Human merges

- [ ] **Step 5: Defer first frontend ticket until skill pack install**

Before the first frontend live run, install the Vercel skills listed in `docs/DESIGN.md`. Defer Impeccable until that ticket unless a design pass needs it earlier.

---

## Execution order

1. Finish and merge `/plan-roadmap` (provides `planner` + `.gitignore`).
2. Execute this plan with Superpowers SDD.
3. Rewrite is complete when Tasks 1–5 are committed and Task 6 static checks pass; Task 7 may remain partially blocked until verification command and Linear auth exist.
