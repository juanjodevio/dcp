# Agent Delivery Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and validate a project-local `/agent-delivery LINEAR-ID` skill that coordinates human-gated planning, implementation, verification, dual review, CTO review, and merge-readiness reporting.

**Architecture:** A single explicit-only Cursor skill owns workflow sequencing and hard stops. Six project custom subagents provide stable named roles; supporting markdown files define shared contracts, report schemas, and dry-run fixtures. Local ignored run files preserve resumable progress, while Linear, GitHub, and steering documents remain canonical.

**Tech Stack:** Cursor Agent Skills, Cursor custom subagents, Markdown/YAML frontmatter, Git, GitHub CLI, Linear MCP, shell verification commands

## Global Constraints

- Run locally and only when explicitly invoked as `/agent-delivery LINEAR-ID`.
- Do not require Cursor Cloud, a coordinator service, PostgreSQL, webhooks, or a credential broker.
- Linear owns scope and status; GitHub owns code, pull requests, reviews, and merges.
- Humans approve plans and merge pull requests.
- Feature branches start from `dev`; milestone pull requests target `main`.
- Reviewer A and CTO use GPT-5.6 Sol.
- Reviewer B uses Claude Opus 5.
- Planner and developer models remain configurable by inheriting the parent model.
- Every delegated role is a fresh run.
- Planner, reviewers, and CTO are read-only.
- A changed head SHA invalidates all earlier verification and review evidence.
- Stop after two unsuccessful code-repair cycles.
- Prompt rules are procedural safeguards, not security boundaries.
- Do not create or configure an external GitHub repository in this plan.
- Do not bootstrap product steering documents in this plan; complete that separate prerequisite before the first real ticket.
- Complete `docs/superpowers/plans/2026-08-25-roadmap-planning-skill.md` first; this plan consumes its shared `.cursor/agents/planner.md`.

---

### Task 1: Add read-only review and governance subagents

**Files:**
- Create: `.cursor/agents/reviewer-a.md`
- Create: `.cursor/agents/reviewer-b.md`
- Create: `.cursor/agents/cto.md`

**Interfaces:**
- Consumes: Bounded context assembled by the parent `agent-delivery` skill
- Produces: Named `reviewer-a`, `reviewer-b`, and `cto` subagents with structured markdown responses

- [ ] **Step 1: Create Reviewer A**

Create `.cursor/agents/reviewer-a.md`:

```markdown
---
name: reviewer-a
description: Independently reviews an exact pull-request SHA for correctness, regressions, tests, and maintainability. Use only when agent-delivery requests Reviewer A.
model: gpt-5.6-sol
readonly: true
---

You are Reviewer A.

Review only the supplied ticket, acceptance criteria, exact diff and head SHA, verification evidence, steering excerpts, ADRs, and repository instructions. Do not request the developer transcript or another reviewer's findings.

Check correctness, edge cases, regressions, security implications, test adequacy, and maintainability. Tie every blocking finding to concrete evidence and a file or behavior.

Do not edit files, run state-changing commands, redefine scope, dismiss another review, or merge. Return the Review Report defined by the caller with exactly one verdict: APPROVE or CHANGES_REQUESTED.
```

- [ ] **Step 2: Create Reviewer B**

Create `.cursor/agents/reviewer-b.md`:

```markdown
---
name: reviewer-b
description: Independently reviews an exact pull-request SHA for correctness, regressions, tests, and maintainability. Use only when agent-delivery requests Reviewer B.
model: claude-opus-5[effort=high]
readonly: true
---

You are Reviewer B.

Review only the supplied ticket, acceptance criteria, exact diff and head SHA, verification evidence, steering excerpts, ADRs, and repository instructions. Do not request the developer transcript or another reviewer's findings.

Check correctness, edge cases, regressions, security implications, test adequacy, and maintainability. Tie every blocking finding to concrete evidence and a file or behavior.

Do not edit files, run state-changing commands, redefine scope, dismiss another review, or merge. Return the Review Report defined by the caller with exactly one verdict: APPROVE or CHANGES_REQUESTED.
```

- [ ] **Step 3: Create the CTO subagent**

Create `.cursor/agents/cto.md`:

```markdown
---
name: cto
description: Reviews an exact pull-request SHA for scope, architecture, roadmap, steering, and ADR drift. Use only when agent-delivery requests the CTO gate.
model: gpt-5.6-sol
readonly: true
---

You are the CTO governance reviewer.

Compare the supplied ticket ancestry, approved scope, exact diff and head SHA, verification evidence, reviewer reports, steering documents, and ADRs.

Evaluate scope drift, product-direction conflicts, architectural drift, missing durable decisions, inappropriate steering edits, and roadmap impact. This is not a third general code review.

Do not edit files, silently reinterpret steering, patch the feature branch, or merge. If steering must change, block the feature and propose a separate human-approved steering change. Return the CTO Report defined by the caller with exactly one verdict: APPROVE, CHANGES_REQUESTED, or STEERING_CHANGE_REQUIRED.
```

- [ ] **Step 4: Validate frontmatter and role restrictions**

Run:

```bash
python - <<'PY'
from pathlib import Path

expected = {
    "reviewer-a.md": ("gpt-5.6-sol", "true"),
    "reviewer-b.md": ("claude-opus-5[effort=high]", "true"),
    "cto.md": ("gpt-5.6-sol", "true"),
}

for filename, (model, readonly) in expected.items():
    text = (Path(".cursor/agents") / filename).read_text()
    assert text.startswith("---\n"), filename
    assert f"model: {model}\n" in text, filename
    assert f"readonly: {readonly}\n" in text, filename
    assert "Do not" in text, filename

print("review and governance agent definitions: OK")
PY
```

Expected: `review and governance agent definitions: OK`.

- [ ] **Step 5: Commit**

```bash
git add .cursor/agents/reviewer-a.md .cursor/agents/reviewer-b.md .cursor/agents/cto.md
git commit -m "feat: define review and governance agents"
```

---

### Task 2: Add writable implementation subagents

**Files:**
- Create: `.cursor/agents/frontend-developer.md`
- Create: `.cursor/agents/backend-developer.md`

**Interfaces:**
- Consumes: One approved atomic ticket, dependency contracts, relevant code, repository guidance, and verification commands
- Produces: A scoped implementation on the assigned feature branch plus an Implementation Report

- [ ] **Step 1: Create the frontend developer**

Create `.cursor/agents/frontend-developer.md`:

```markdown
---
name: frontend-developer
description: Implements one approved frontend Linear ticket on its assigned feature branch. Use only when agent-delivery dispatches frontend work or repairs.
model: inherit
readonly: false
---

You are the frontend implementation agent.

Implement only the supplied approved ticket. Follow the supplied acceptance criteria, UI contract, steering documents, ADRs, repository instructions, and verification commands.

Prefer focused components and preserve existing design patterns. Add or update tests for changed behavior. Run the required checks and report exact evidence.

You may edit code and tests and create scoped commits on the assigned feature branch. Do not merge, approve, expand scope, edit steering artifacts, silently change an interface, or touch unrelated user changes. Return the Implementation Report defined by the caller.
```

- [ ] **Step 2: Create the backend developer**

Create `.cursor/agents/backend-developer.md`:

```markdown
---
name: backend-developer
description: Implements one approved backend Linear ticket on its assigned feature branch. Use only when agent-delivery dispatches backend work or repairs.
model: inherit
readonly: false
---

You are the backend implementation agent.

Implement only the supplied approved ticket. Follow the supplied acceptance criteria, API or data contract, steering documents, ADRs, repository instructions, and verification commands.

Prefer focused modules and preserve existing architecture. Add or update tests for changed behavior. Run the required checks and report exact evidence.

You may edit code and tests and create scoped commits on the assigned feature branch. Do not merge, approve, expand scope, edit steering artifacts, silently change an interface, or touch unrelated user changes. Return the Implementation Report defined by the caller.
```

- [ ] **Step 3: Validate writable role configuration**

Run:

```bash
python - <<'PY'
from pathlib import Path

for filename in ("frontend-developer.md", "backend-developer.md"):
    text = (Path(".cursor/agents") / filename).read_text()
    assert "model: inherit\n" in text, filename
    assert "readonly: false\n" in text, filename
    assert "Do not merge" in text, filename

print("developer agent definitions: OK")
PY
```

Expected: `developer agent definitions: OK`.

- [ ] **Step 4: Commit**

```bash
git add .cursor/agents/frontend-developer.md .cursor/agents/backend-developer.md
git commit -m "feat: define frontend and backend agents"
```

---

### Task 3: Define shared role contracts and report schemas

**Files:**
- Create: `.cursor/skills/agent-delivery/ROLE-CONTRACTS.md`
- Create: `.cursor/skills/agent-delivery/REPORT-TEMPLATES.md`

**Interfaces:**
- Consumes: Role-specific prompts and the approved workflow specification
- Produces: Canonical context boundaries and parseable report formats used by `SKILL.md`

- [ ] **Step 1: Write the shared role contracts**

Create `.cursor/skills/agent-delivery/ROLE-CONTRACTS.md`:

```markdown
# Agent Delivery Role Contracts

## Shared invariants

- Every role run is fresh.
- Every report names the Linear ticket and exact Git SHA it evaluated.
- Only canonical Linear, GitHub, steering, ADR, and repository evidence may determine a gate.
- Missing evidence produces BLOCKED, never an inferred success.
- A new SHA invalidates verification and all reviews for the previous SHA.

## Planner

Input: parent ticket, steering documents, ADRs, repository map.
Output: Planner Report.
Writes: none.
Hard stop: ambiguous product intent or an unresolvable steering conflict.

## Frontend developer

Input: one approved frontend ticket, UI contract, relevant code, repository guidance, verification command.
Output: Implementation Report.
Writes: scoped code and tests on the assigned feature branch.
Hard stop: required scope or interface change.

## Backend developer

Input: one approved backend ticket, API/data contract, relevant code, repository guidance, verification command.
Output: Implementation Report.
Writes: scoped code and tests on the assigned feature branch.
Hard stop: required scope, schema, or interface change not approved by the ticket.

## Reviewer A and Reviewer B

Input: ticket, acceptance criteria, exact diff and SHA, verification evidence, relevant steering and ADRs.
Output: Review Report.
Writes: none.
Isolation: no developer transcript and no other reviewer report.

## CTO

Input: ticket ancestry, exact diff and SHA, verification evidence, both review reports, all steering documents and ADRs.
Output: CTO Report.
Writes: none.
Boundary: governance and drift only, not a third general code review.

## Human

Approves plans, changes Linear status, resolves blocked states, approves steering changes, and merges pull requests.
```

- [ ] **Step 2: Write the report templates**

Create `.cursor/skills/agent-delivery/REPORT-TEMPLATES.md`:

```markdown
# Agent Delivery Report Templates

Use every heading. Write `None` when a non-verdict section has no entries.

## Planner Report

### Ticket
### Atomicity
Use `ATOMIC`, `DECOMPOSE`, or `BLOCKED`.
### Proposed children
### Dependency edges
### Interface contracts
### Integration ticket
### Risks
### Steering references
### Human decision required

## Implementation Report

### Ticket
### Role
### Branch
### Head SHA
### Files changed
### Behavior implemented
### Tests changed
### Verification performed
### Scope or contract concerns
### Result
Use `READY_FOR_VERIFICATION` or `BLOCKED`.

## Verification Report

### Ticket
### Head SHA
### Commands
### Exit statuses
### Failure evidence
### Result
Use `PASS` or `FAIL`.

## Review Report

### Ticket
### Reviewer
### Head SHA
### Blocking findings
### Non-blocking observations
### Evidence checked
### Verdict
Use `APPROVE` or `CHANGES_REQUESTED`.

## CTO Report

### Ticket
### Head SHA
### Scope assessment
### Architecture assessment
### Steering and ADR assessment
### Roadmap impact
### Required steering change
### Verdict
Use `APPROVE`, `CHANGES_REQUESTED`, or `STEERING_CHANGE_REQUIRED`.

## Repair Report

### Ticket
### Repair cycle
### Previous SHA
### New SHA
### Blocking evidence addressed
### Remaining blockers
### Result
Use `READY_FOR_REVERIFICATION` or `BLOCKED`.

## Merge-Readiness Report

### Ticket and approved plan
### Pull request
### Branch and head SHA
### Verification evidence
### Reviewer A verdict
### Reviewer B verdict
### CTO verdict
### Repair history
### Unresolved non-blocking risks
### Human actions
### Result
Use `MERGE_READY` or `BLOCKED`.
```

- [ ] **Step 3: Validate report verdict vocabularies**

Run:

```bash
python - <<'PY'
from pathlib import Path

text = Path(".cursor/skills/agent-delivery/REPORT-TEMPLATES.md").read_text()
for verdict in (
    "ATOMIC",
    "DECOMPOSE",
    "READY_FOR_VERIFICATION",
    "PASS",
    "CHANGES_REQUESTED",
    "STEERING_CHANGE_REQUIRED",
    "READY_FOR_REVERIFICATION",
    "MERGE_READY",
):
    assert verdict in text, verdict

print("report templates: OK")
PY
```

Expected: `report templates: OK`.

- [ ] **Step 4: Commit**

```bash
git add .cursor/skills/agent-delivery/ROLE-CONTRACTS.md .cursor/skills/agent-delivery/REPORT-TEMPLATES.md
git commit -m "feat: define agent delivery contracts"
```

---

### Task 4: Define dry-run workflow fixtures

**Files:**
- Create: `.cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md`

**Interfaces:**
- Consumes: The state transitions and gate semantics implemented by `SKILL.md`
- Produces: Eight deterministic scenarios for validating dispatch, invalidation, repair, and blocking behavior without external writes

- [ ] **Step 1: Create the dry-run scenarios**

Create `.cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md`:

```markdown
# Agent Delivery Dry-Run Scenarios

Dry runs simulate state transitions. They do not call Linear, modify Git, create pull requests, or write outside `.agent-delivery/runs/`.

## atomic-backend

State: Agent Ready.
Evidence: explicit API acceptance criteria and verification command.
Expected: backend developer dispatch, verification, both reviewers, CTO, MERGE_READY.

## requires-decomposition

State: Needs Planning.
Evidence: one parent requests an API and a web interface.
Expected: planner returns DECOMPOSE with backend, frontend, and integration children; workflow stops for human approval.

## missing-acceptance-criteria

State: Agent Ready.
Evidence: desired behavior is not measurable.
Expected: BLOCKED before developer dispatch.

## verification-failure

State: Agent Ready.
Evidence: implementation report is complete; verification exit status is 1.
Expected: repair cycle 1 begins; reviews do not run.

## reviewer-disagreement

State: Agent Ready.
Evidence: verification passes; Reviewer A approves; Reviewer B requests changes.
Expected: repair cycle 1 begins; CTO cannot make the change request disappear.

## steering-drift

State: Agent Ready.
Evidence: code introduces a hard Kubernetes dependency contrary to TECH.md.
Expected: CTO returns STEERING_CHANGE_REQUIRED; feature stops for a separate human-approved steering change.

## stale-evidence

State: Agent Ready.
Evidence: SHA one passes all gates; repair pushes SHA two.
Expected: every SHA-one verification and review result becomes stale; all gates rerun against SHA two.

## repair-limit

State: Agent Ready.
Evidence: two code-changing repair cycles fail verification or review.
Expected: Blocked — Human; no third repair dispatch.
```

- [ ] **Step 2: Validate scenario coverage**

Run:

```bash
python - <<'PY'
from pathlib import Path

text = Path(".cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md").read_text()
names = (
    "atomic-backend",
    "requires-decomposition",
    "missing-acceptance-criteria",
    "verification-failure",
    "reviewer-disagreement",
    "steering-drift",
    "stale-evidence",
    "repair-limit",
)
for name in names:
    assert f"## {name}\n" in text, name
assert text.count("## ") == 8

print("dry-run scenarios: OK")
PY
```

Expected: `dry-run scenarios: OK`.

- [ ] **Step 3: Commit**

```bash
git add .cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md
git commit -m "test: add agent delivery dry-run scenarios"
```

---

### Task 5: Implement the explicit agent-delivery skill

**Files:**
- Create: `.cursor/skills/agent-delivery/SKILL.md`

**Interfaces:**
- Consumes: `/agent-delivery LINEAR-ID` or `/agent-delivery DRY-RUN scenario-name`, custom subagents, contracts, templates, Linear MCP, Git, `gh`, and the repository verification command
- Produces: Planner, implementation, verification, review, repair, CTO, and merge-readiness reports plus ignored local run state

- [ ] **Step 1: Create the skill**

Create `.cursor/skills/agent-delivery/SKILL.md`:

```markdown
---
name: agent-delivery
description: Coordinates the repository's human-gated Linear-to-GitHub delivery workflow. Invoke explicitly as /agent-delivery LINEAR-ID or /agent-delivery DRY-RUN scenario-name.
disable-model-invocation: true
icon: git-branch
color: purple
---

# Agent Delivery

Coordinate one ticket. Never weaken a gate to make progress.

Read [ROLE-CONTRACTS.md](ROLE-CONTRACTS.md) and [REPORT-TEMPLATES.md](REPORT-TEMPLATES.md) before dispatching roles.

## Parse the invocation

Accept exactly:

- `/agent-delivery LINEAR-ID`
- `/agent-delivery DRY-RUN scenario-name`

If the argument is missing or malformed, show these forms and stop.

For a dry run, read [DRY-RUN-SCENARIOS.md](DRY-RUN-SCENARIOS.md), simulate only the named scenario, write evidence under `.agent-delivery/runs/dry-run-<scenario-name>/`, and perform no external writes.

## Shared safety rules

- Linear owns scope and status.
- GitHub owns commits, pull requests, reviews, and merges.
- Steering documents and ADRs own durable direction.
- Humans approve plans and merge pull requests.
- Do not push directly to `dev` or `main`.
- Do not merge.
- Do not overwrite unrelated local changes.
- Every delegated role must be a fresh custom subagent run.
- A result applies only to the exact SHA named in its report.
- A new SHA invalidates all earlier verification, Reviewer A, Reviewer B, and CTO evidence.
- Any missing evidence, ambiguous requirement, unresolved dependency, or steering conflict is BLOCKED.
- Allow at most two code-changing repair cycles.

## Create the run record

Use `.agent-delivery/runs/<ticket-id>/`.

Maintain:

- `run.md`
- `plan.md` when planning occurs
- `verification.md`
- `review-a.md`
- `review-b.md`
- `cto-review.md`
- `repairs.md`
- `merge-readiness.md`

Record ticket, phase, role models, branch, pull request, current SHA, evidence SHA, and repair count. Never store credentials.

## Load canonical context

1. Read root `AGENTS.md`.
2. Follow its links to PRODUCT, TECH, DESIGN, ROADMAP, STRUCTURE, and ADRs.
3. Retrieve the Linear ticket, parent, children, dependencies, state, and acceptance criteria.
4. Read relevant repository files without broad unrelated loading.
5. Determine the single verification command from `AGENTS.md`.

Stop if a required source is missing.

## Route by Linear state

### Needs Planning

Launch the `planner` custom subagent with the bounded canonical context and Planner Report template.

Save `plan.md`, present the proposal, and stop. The planner and parent workflow may not mark the ticket Agent Ready.

### Agent Ready

Confirm the ticket is atomic or has a human-approved child plan. Confirm dependencies are complete.

If the ticket is not ready, return BLOCKED and stop.

Any other Linear state is ineligible. Report the accepted states and stop.

## Preflight implementation

1. Confirm the current repository is the ticket's repository.
2. Confirm `dev` exists locally and matches the intended base.
3. Inspect worktree status.
4. Preserve unrelated user changes by creating a separate worktree when needed.
5. Select `frontend-developer` or `backend-developer` from ticket scope.
6. Create `feat/<linear-id>-<short-slug>` from `dev`.
7. Record the base SHA, branch, role, and repair count zero.

Stop if isolation cannot be established safely.

## Implement

Launch the selected developer with one approved ticket, contracts, relevant context, verification command, and Implementation Report template.

Require `READY_FOR_VERIFICATION`. Confirm changes remain in scope. Resolve the exact head SHA and write it to `run.md`.

## Verify

Run the exact command documented by `AGENTS.md`. Record command, times, exit status, concise output, and head SHA in `verification.md`.

On failure, enter the repair loop before launching reviews.

## Open or update the pull request

After verification passes:

1. Confirm all scoped changes are committed.
2. Push only the feature branch.
3. Open or update a GitHub pull request targeting `dev`.
4. Include the Linear ticket, implementation summary, exact SHA, and verification evidence in the pull-request body.
5. Record the pull-request URL in `run.md`.

Do not merge or enable auto-merge.

## Review

Only after verification passes, launch fresh `reviewer-a` and `reviewer-b` custom subagents independently. Give both the same ticket, acceptance criteria, exact diff and SHA, verification evidence, steering excerpts, ADRs, and Review Report template.

Do not give either reviewer the developer transcript or the other review.

Save both reports. Any CHANGES_REQUESTED verdict enters the repair loop.

## CTO gate

After both code reviews exist, launch the fresh `cto` custom subagent with ticket ancestry, exact diff and SHA, verification evidence, both reviewer reports, all steering documents, ADRs, and the CTO Report template.

- APPROVE continues.
- CHANGES_REQUESTED enters the repair loop.
- STEERING_CHANGE_REQUIRED blocks the feature and requests a separate human-approved steering change.

## Repair loop

Increment the repair count only when code changes.

If the count would exceed two, set the result to `Blocked — Human`, summarize all evidence, and stop.

Launch a fresh developer of the original role with the ticket, current diff and SHA, all blocking evidence, repository guidance, and Repair Report template.

After a code change:

1. Resolve the new SHA.
2. Mark all previous verification and review evidence stale.
3. Run verification again.
4. Launch fresh Reviewer A and Reviewer B again.
5. Launch a fresh CTO again.

Transient execution failures may retry without consuming a repair cycle when no code changed.

## Produce merge readiness

Require all evidence to name the current SHA and contain:

- verification PASS;
- Reviewer A APPROVE;
- Reviewer B APPROVE; and
- CTO APPROVE.

Write `merge-readiness.md` from the Merge-Readiness Report template. Post durable role-labeled summaries to the GitHub pull request when one exists.

Return MERGE_READY with explicit human instructions to inspect and merge into `dev`. Never merge.
```

- [ ] **Step 2: Validate skill discovery metadata**

Run:

```bash
python - <<'PY'
from pathlib import Path

path = Path(".cursor/skills/agent-delivery/SKILL.md")
text = path.read_text()

assert text.startswith("---\n")
assert "name: agent-delivery\n" in text
assert "disable-model-invocation: true\n" in text
assert "/agent-delivery LINEAR-ID" in text
assert "Allow at most two code-changing repair cycles." in text
assert "Never merge." in text
assert len(text.splitlines()) < 500

for reference in (
    "ROLE-CONTRACTS.md",
    "REPORT-TEMPLATES.md",
    "DRY-RUN-SCENARIOS.md",
):
    assert reference in text
    assert path.with_name(reference).is_file()

print("agent-delivery skill: OK")
PY
```

Expected: `agent-delivery skill: OK`.

- [ ] **Step 3: Scan for forbidden unfinished language**

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

paths = list(Path(".cursor/skills/agent-delivery").glob("*.md"))
paths.extend(Path(".cursor/agents").glob("*.md"))

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
git add .cursor/skills/agent-delivery/SKILL.md
git commit -m "feat: add local agent delivery workflow"
```

---

### Task 6: Validate discovery and dry-run gates

**Files:**
- Modify only if validation exposes a defect:
  - `.cursor/skills/agent-delivery/SKILL.md`
  - `.cursor/skills/agent-delivery/ROLE-CONTRACTS.md`
  - `.cursor/skills/agent-delivery/REPORT-TEMPLATES.md`
  - `.cursor/skills/agent-delivery/DRY-RUN-SCENARIOS.md`
  - `.cursor/agents/*.md`
- Create ignored evidence under: `.agent-delivery/runs/`

**Interfaces:**
- Consumes: Cursor's skill discovery, custom subagent discovery, and the eight dry-run fixtures
- Produces: Evidence that the workflow dispatches the correct roles and fails closed at each gate

- [ ] **Step 1: Restart or open a fresh Cursor Agent chat**

Open the skill picker and verify `agent-delivery` appears. Open the available subagent list and verify:

```text
planner
frontend-developer
backend-developer
reviewer-a
reviewer-b
cto
```

Expected: the skill and all six project subagents are discoverable.

- [ ] **Step 2: Verify malformed invocation fails closed**

Invoke:

```text
/agent-delivery
```

Expected: usage shows the two accepted invocation forms and no external or repository mutation occurs.

- [ ] **Step 3: Run the planning dry run**

Invoke:

```text
/agent-delivery DRY-RUN requires-decomposition
```

Expected: planner output proposes backend, frontend, and integration children, then stops for human approval.

- [ ] **Step 4: Run the successful atomic dry run**

Invoke:

```text
/agent-delivery DRY-RUN atomic-backend
```

Expected: simulated backend implementation, PASS verification, two independent approvals, CTO approval, and MERGE_READY.

- [ ] **Step 5: Run each blocking scenario**

Invoke each:

```text
/agent-delivery DRY-RUN missing-acceptance-criteria
/agent-delivery DRY-RUN verification-failure
/agent-delivery DRY-RUN reviewer-disagreement
/agent-delivery DRY-RUN steering-drift
/agent-delivery DRY-RUN stale-evidence
/agent-delivery DRY-RUN repair-limit
```

Expected:

- missing acceptance criteria blocks before implementation;
- verification failure skips reviews and starts repair;
- reviewer disagreement cannot be overridden by the CTO;
- steering drift requires a separate human-approved steering change;
- new-SHA evidence invalidates old-SHA evidence; and
- the repair limit stops before a third code-changing repair.

- [ ] **Step 6: Inspect ignored evidence and repository cleanliness**

Run:

```bash
git status --short
git check-ignore -v .agent-delivery/runs
```

Expected: no dry-run evidence appears in Git status, and `.gitignore` is the matching rule.

- [ ] **Step 7: Fix validation defects and rerun only affected scenarios**

For each defect, change the smallest relevant prompt or template, then rerun the scenario that exposed it. Do not weaken expected gate behavior.

- [ ] **Step 8: Commit validation fixes if any**

If files changed:

```bash
git add .cursor/skills/agent-delivery .cursor/agents
git commit -m "fix: enforce agent delivery gates"
```

If no files changed, do not create an empty commit.

---

### Task 7: Prepare first real-ticket prerequisites

**Files:**
- Verify: `AGENTS.md`
- Verify: `docs/PRODUCT.md`
- Verify: `docs/TECH.md`
- Verify: `docs/DESIGN.md`
- Verify: `docs/ROADMAP.md`
- Verify: `docs/STRUCTURE.md`
- Verify: `docs/adr/`

**Interfaces:**
- Consumes: Separately approved product-steering artifacts, Linear workflow configuration, GitHub remote, protected branches, and one stable repository verification command
- Produces: A binary readiness decision for the first real `/agent-delivery LINEAR-ID` run

- [ ] **Step 1: Verify steering prerequisites**

Run:

```bash
python - <<'PY'
from pathlib import Path

required = (
    "AGENTS.md",
    "docs/PRODUCT.md",
    "docs/TECH.md",
    "docs/DESIGN.md",
    "docs/ROADMAP.md",
    "docs/STRUCTURE.md",
)

missing = [path for path in required if not Path(path).is_file()]
assert not missing, f"missing steering files: {missing}"
assert Path("docs/adr").is_dir(), "missing docs/adr/"

print("steering prerequisites: OK")
PY
```

Expected after the separate product-steering work: `steering prerequisites: OK`.

- [ ] **Step 2: Verify GitHub and branch prerequisites**

Run:

```bash
gh auth status
gh repo view --json nameWithOwner,url
git show-ref --verify refs/heads/dev
git show-ref --verify refs/heads/main
```

Expected: authenticated GitHub CLI, a repository URL, and both local branches. If any command fails, stop; do not create external resources or branches without human approval.

- [ ] **Step 3: Verify Linear workflow prerequisites**

Using the configured Linear integration, confirm the target team has these exact states:

```text
Needs Planning
Agent Ready
Blocked — Human
```

Expected: all three states exist. If one is missing, stop and ask a Linear administrator to add it.

- [ ] **Step 4: Verify the repository command contract**

Read `AGENTS.md`, extract its single verification command, and run it.

Expected: exit code `0`. If no command is documented or the command fails, the repository is not ready for a real ticket.

- [ ] **Step 5: Report readiness**

Produce a concise result containing:

```text
Steering: READY or BLOCKED
GitHub: READY or BLOCKED
Branches: READY or BLOCKED
Linear states: READY or BLOCKED
Verification command: READY or BLOCKED
First real ticket: READY or BLOCKED
```

Do not run a real ticket until every line is `READY`.
