# Local-First Agent Delivery Workflow

**Date:** 2026-08-25  
**Status:** Approved  
**Revised:** 2026-08-25 — thin `/agent-delivery` wraps Superpowers for backend delivery; keep a specialized frontend implementer

## Purpose

Validate an agent-driven software delivery workflow without first building an orchestration platform.

The initial system uses two project-local Cursor skills invoked manually:

```text
/plan-roadmap
/agent-delivery LINEAR-ID
```

`/plan-roadmap` turns the approved roadmap into milestones and draft Linear work. `/agent-delivery` is a thin orchestrator: it owns Linear and GitHub gates, then reuses Superpowers skills for implementation, review, and branch finish. Humans approve roadmap changes, move tickets to `Agent Ready`, resolve ambiguity, and merge pull requests. Automation is added only after repeated manual runs reveal stable transitions worth automating.

## Decisions

- Linear is the canonical source for work scope, acceptance criteria, dependencies, and status.
- GitHub is the canonical Git forge, pull-request system, and merge record.
- Product steering documents and ADRs are the canonical sources for durable product and technical direction.
- The version of `docs/ROADMAP.md` merged into `main` authorizes the Planner to create and refine corresponding draft Linear work without a second planning approval.
- The first version runs locally in Cursor and is started manually.
- The workflows live in `.cursor/skills/plan-roadmap/` and `.cursor/skills/agent-delivery/` in the product repository.
- Feature branches target `dev`. Milestone release pull requests target `main`.
- Humans merge into both `dev` and `main` during the bootstrap phase.
- Backend implementation reuses Superpowers `subagent-driven-development` with its stock implementer prompt.
- Frontend implementation reuses the same Superpowers delivery loop, but dispatches the project `frontend-developer` agent (specialized design packet) instead of the stock implementer.
- Code review and branch completion reuse Superpowers `requesting-code-review` and `finishing-a-development-branch`.
- Optional planning for a `Needs Planning` ticket reuses Superpowers `writing-plans` when a repo implementation plan is needed; Linear draft decomposition still uses the shared Planner.
- A thin project CTO gate remains for scope and steering drift after code review.
- Planner and developer models are configurable by role.
- Every role invocation is a fresh, bounded run.
- Two unsuccessful repair cycles stop the workflow for human intervention.
- Do not reinvent Superpowers implement/review/finish mechanics inside project skills.

## Why GitHub

GitHub is preferable to Cursor Origin for the bootstrap workflow because it provides mature pull requests, branch protection, Actions, self-hosted runners, Apps, checks, and public open-source collaboration. Cursor Cloud Agents and Cursor Automations also integrate with GitHub.

Cursor Origin remains an option for later evaluation. The skill must avoid forge-specific assumptions where practical, but v0.1 may use `git` and `gh` directly because GitHub is the selected forge.

## Scope

### Included

- Manual roadmap-to-milestone planning
- Creation and refinement of draft Linear tickets from the approved roadmap
- Roadmap coverage and milestone-drift reporting
- Manual skill invocation with a Linear ticket identifier
- Optional ticket decomposition by a planner
- Human approval of generated delivery plans
- One isolated feature branch or worktree per implementation task
- Backend delivery via Superpowers SDD + stock implementer
- Frontend delivery via Superpowers SDD loop with `frontend-developer` implementer packet
- Local deterministic verification
- Superpowers code review, plus a thin CTO scope/steering-drift gate
- At most two repair cycles
- Merge-readiness reporting via Superpowers finish flow plus Linear/GitHub status notes
- Human merge into `dev`
- Human-approved milestone pull requests from `dev` to `main`

### Deferred

- Linear-triggered Cursor Automation
- Cursor Cloud execution
- A coordinator service or daemon
- PostgreSQL workflow state
- Webhook ingestion
- Credential broker
- Distinct GitHub App identities for every role
- Automated merging
- A generalized CI workflow language
- A separate delivery-platform repository
- Durable multi-ticket scheduling and concurrent orchestration
- Custom project `backend-developer`, `reviewer-a`, and `reviewer-b` agents (replaced by Superpowers)

### Non-goals

- Treating prompts as security boundaries
- Letting agents redefine ticket scope
- Letting implementation agents edit steering documents
- Letting reviewers patch code they review
- Replacing Linear or GitHub with a custom task or pull-request system
- Building a general autonomous-company control plane
- Forking or overwriting Superpowers plugin skills for ordinary backend delivery

## Sources of Truth

Each kind of state has one canonical owner:

- **Scope and status:** Linear
- **Code, commits, reviews, and merges:** GitHub
- **Product and technical direction:** `docs/PRODUCT.md`, `docs/TECH.md`, `docs/DESIGN.md`, `docs/ROADMAP.md`, `docs/STRUCTURE.md`, and `docs/adr/`
- **Agent orientation:** root `AGENTS.md`
- **Temporary workflow progress:** ignored `.agent-delivery/runs/<ticket-id>/`

Temporary run state is a convenience for resuming local work. It does not override Linear, GitHub, steering documents, or ADRs.

## Prerequisites

Before the first real delivery run, the repository must have:

- the steering documents listed above, bootstrapped from the existing session handoff and approved by a human;
- a root `AGENTS.md` that points agents to those documents;
- `dev` and `main` branches with direct pushes blocked;
- a GitHub remote and authenticated `gh` CLI;
- Linear states named `Needs Planning`, `Agent Ready`, and `Blocked — Human`;
- one verification command documented in `AGENTS.md`;
- the Superpowers plugin available in Cursor (SDD, writing-plans, requesting-code-review, finishing-a-development-branch, using-git-worktrees as needed); and
- `.agent-delivery/` excluded from Git.

The verification command may call several underlying tools, but the skill invokes one stable entrypoint. The implementation plan will select its exact command after the application scaffold and package tooling are chosen.

## Skill Structure

The initial skill consists of:

```text
.cursor/skills/agent-delivery/
  SKILL.md
  ROLE-CONTRACTS.md
  REPORT-TEMPLATES.md

.cursor/skills/plan-roadmap/
  SKILL.md
  MILESTONE-TEMPLATES.md
  DRY-RUN-SCENARIOS.md

.cursor/agents/
  planner.md
  frontend-developer.md
  cto.md
```

`/agent-delivery` `SKILL.md` is explicit-only and uses `disable-model-invocation: true`. It defines Linear eligibility, role selection, hard stops, repair limit, context assembly, and handoffs into Superpowers skills. It does not reimplement SDD, code review, or branch-finish procedures.

`ROLE-CONTRACTS.md` defines each project role's inputs, outputs, allowed actions, and prohibited actions, and names which Superpowers skills replace former custom roles.

`REPORT-TEMPLATES.md` defines planner, CTO, repair, Linear status, and merge-readiness outputs that Superpowers does not already own.

`MILESTONE-TEMPLATES.md` defines roadmap authoring forms, required parsing patterns, malformed declaration detectors, sync-key exactness, milestone activity derivation, and the roadmap coverage, milestone plan, Linear ticket, dependency, and reconciliation outputs. It is the single canonical place those forms are stated; no other document restates them.

Only a line that claims to be a declaration can block parsing. A heading such as `### Deliverables for M1` and a sentence or link that merely mentions `[M1-D2]` are not declarations and never block.

`DRY-RUN-SCENARIOS.md` defines the named roadmap planning fixtures. Its second-level headings are the complete set of valid scenario names, and an unknown name lists the valid names and stops.

### Project agents vs Superpowers

| Concern | Owner |
| --- | --- |
| Roadmap ↔ Linear draft sync | `/plan-roadmap` + `planner` |
| Linear eligibility, Agent Ready gate, repair cap, run records | `/agent-delivery` |
| Backend implementer | Superpowers SDD stock `implementer-prompt.md` |
| Frontend implementer | project `frontend-developer` (SDD loop, specialized packet) |
| Task/branch code review | Superpowers `requesting-code-review` |
| Scope / steering drift | project `cto` |
| Worktree isolation | Superpowers `using-git-worktrees` when needed |
| PR / finish options | Superpowers `finishing-a-development-branch` |
| Repo implementation plans | Superpowers `writing-plans` |

Do not create project `backend-developer`, `reviewer-a`, or `reviewer-b` agents.

`frontend-developer.md` inherits the parent model and is the specialized implementer packet for UI tickets. It must require `docs/DESIGN.md` and relevant product screens before edits, apply the project's UI composition rules, and must not invent a brand system while `DESIGN.md` still defers one. It does not overwrite Superpowers plugin files; `/agent-delivery` selects it when filling the SDD implementer dispatch `## Context` / prompt body for frontend work.

Before the first UI ticket, install the frontend skill pack noted in `docs/DESIGN.md` (`vercel-composition-patterns`, `web-design-guidelines`, `react-best-practices`). Defer `npx impeccable install` (+ `/impeccable init`) until that first UI ticket unless a design pass needs it earlier.

`planner.md` and `cto.md` are read-only. The CTO pins GPT-5.6 Sol. Planner inherits the selected parent model.

No executable helper scripts are required initially. Stable repeated operations may be extracted after the workflow has been exercised.

## Roadmap Planning Workflow

`/plan-roadmap` reads the approved `docs/ROADMAP.md` from `main`, then compares every active milestone with existing Linear projects, milestones, and tickets.

The Planner:

1. turns roadmap outcomes into dependency-ordered deliverables;
2. identifies backend, frontend, integration, migration, documentation, and operational work;
3. defines acceptance criteria, contracts, verification requirements, risks, and milestone dependencies;
4. creates missing Linear tickets in `Draft` or `Needs Planning`;
5. refines existing tickets only while they remain in `Draft` or `Needs Planning`;
6. links every ticket to its roadmap milestone using a stable roadmap identifier; and
7. reports coverage gaps, stale tickets, conflicts, and milestone drift.

The approved roadmap is sufficient authorization for these draft mutations. Planner does not require a second human approval before creating or refining draft tickets.

Planner may not:

- change `ROADMAP.md` or product intent;
- move any ticket to `Agent Ready`;
- rewrite tickets already in `Agent Ready` or an active delivery state;
- delete, cancel, or close work;
- resolve roadmap contradictions by assumption; or
- implement code.

Duplicate roadmap keys, duplicate Linear sync keys, unproven roadmap authority, and unproven search scope or pagination fail closed on every run, including a run scoped to a single milestone. Stale detection is always global.

After a live run creates tickets, the workflow opens one mechanical roadmap-link pull request from a dedicated branch into `main`. It may add only `Linear tickets:` reference lines, appending to a milestone's existing reference line in place rather than adding a second one, and it is merged by a human. Its self-check inspects every added, changed, and removed diff line: the only permitted deletion is an existing `Linear tickets:` line being replaced in place, and any deletion of roadmap intent discards the branch and blocks. An orphan link branch from an interrupted run is reused only when it targets the same authority commit and passes the same self-check; otherwise it is left untouched and reported for human cleanup, and it is never deleted or force-updated. When GitHub is unavailable, the branch stays local and unmerged and the run reports PARTIAL or BLOCKED with the exact setup action.

Conflicts between the approved roadmap and current Linear state produce a reconciliation report for a human. The workflow is idempotent: rerunning it updates matching draft work instead of creating duplicates.

## Ticket Invocation and Status Rules

The command is valid for two Linear states.

### `Needs Planning`

The skill:

1. Reads the parent ticket, steering documents, ADRs, and repository structure.
2. Launches a fresh planner for Linear decomposition when child tickets or contracts are missing.
3. When a repository implementation plan is also needed, invokes Superpowers `writing-plans` and stores the plan under `docs/superpowers/plans/`.
4. Publishes or presents the proposal.
5. Stops.

The planner may create or refine child tickets in `Draft` or `Needs Planning`. It cannot mark its own plan ready. A human reviews the resulting ticket set and moves eligible work to `Agent Ready`.

### `Agent Ready`

The skill verifies that the ticket is either:

- atomic, with explicit acceptance criteria, interfaces, and verification steps; or
- backed by a human-approved child-ticket plan.

If neither condition holds, the skill fails closed and requests planning. Otherwise, it proceeds with delivery through Superpowers.

## Delivery Flow

`/agent-delivery` owns preflight, role selection, Linear status updates, the repair cap, the CTO gate, and run records. Superpowers owns implement → review → finish mechanics.

```text
/agent-delivery LINEAR-ID
  Needs Planning → planner and/or writing-plans → stop for human Agent Ready
  Agent Ready →
      backend  → Superpowers SDD (stock implementer)
      frontend → Superpowers SDD (frontend-developer packet)
      then     → Superpowers requesting-code-review
               → project cto (scope / steering drift)
               → Superpowers finishing-a-development-branch (PR toward dev)
               → Linear status / merge-readiness notes
```

### 1. Preflight

The skill:

- loads `AGENTS.md` and relevant steering documents;
- retrieves the Linear ticket and approved descendants;
- confirms the ticket is eligible to run;
- checks for unresolved dependencies;
- classifies the ticket as frontend, backend, or integration;
- confirms a deterministic verification entrypoint exists;
- confirms required Superpowers skills are available;
- records the selected role-model configuration;
- identifies the `dev` base SHA; and
- creates or resumes the local run record.

Missing intent, conflicting steering, a missing verification command, missing Superpowers skills, or an unclean unsafe workspace blocks execution.

### 2. Isolated implementation

The skill creates or resumes a feature branch from the current `dev` branch, using Superpowers `using-git-worktrees` when isolation is required. The expected naming convention is:

```text
feat/<linear-id>-<short-slug>
```

**Backend tickets** dispatch Superpowers SDD with the stock implementer prompt. The implementer receives only the approved ticket context, acceptance criteria, steering/ADR excerpts, dependency contracts, repository instructions, relevant code context, and verification commands.

**Frontend tickets** use the same SDD process and file-handoff rules, but the controller fills the implementer dispatch from `.cursor/agents/frontend-developer.md` instead of the stock implementer body. That packet adds required design reads and UI composition constraints. Do not edit Superpowers plugin files to achieve this.

The implementer works one approved work item, runs local checks, commits, and returns evidence. It cannot merge, approve, expand scope, or edit steering artifacts.

### 3. Deterministic verification

Verification follows the plan and Superpowers SDD / verification practices against the exact feature-branch SHA.

The repository's versioned verification entrypoint should eventually cover formatting, linting, static types, unit tests, and relevant integration tests. Until the product repository defines that entrypoint, delivery must stop rather than inventing an unverifiable success claim.

Verification evidence records:

- command;
- start and completion time;
- exit status;
- tested SHA; and
- concise failure output or success summary.

### 4. Independent reviews

After deterministic checks pass, the skill:

1. Invokes Superpowers `requesting-code-review` for the task or whole-branch review package.
2. Launches a fresh project `cto` run for scope and steering drift only.

The code reviewer receives the approved ticket and acceptance criteria, the exact diff and head SHA, verification evidence, and relevant steering. It does not receive the developer transcript.

During local bootstrap, review verdicts are role-labeled reports under the human's GitHub identity. They are not independent GitHub-account approvals. Distinct enforceable reviewer identities are deferred.

The CTO reviewer receives ticket ancestry, scope, the diff, the head SHA, steering documents, ADRs, verification evidence, and the code-review report. The CTO evaluates:

- scope drift;
- contradictions with product direction;
- architectural drift;
- missing durable decisions;
- inappropriate steering changes; and
- milestone or roadmap impact.

The CTO does not perform a second general code review. Dual custom Reviewer A / Reviewer B agents are not part of v0.1.

### 5. Repair loop

Any failed deterministic check or blocking review / CTO verdict blocks merge readiness.

The skill launches a fresh repair through the same implementer path used for the ticket (stock SDD implementer for backend, `frontend-developer` packet for frontend) with:

- the approved ticket;
- the current diff and SHA;
- failing verification evidence;
- all blocking findings; and
- relevant repository guidance.

A pushed repair creates a new SHA. All previous checks and reviews become stale and must run again.

Two unsuccessful repair cycles result in `Blocked — Human`. Transient tool or infrastructure failures may be retried and do not count as repair cycles unless they produce a code change.

### 6. Merge readiness

When gates pass, the skill invokes Superpowers `finishing-a-development-branch` for PR options toward `dev`, then writes a merge-readiness note containing:

- Linear ticket and approved plan;
- branch, pull-request link, and exact SHA;
- verification evidence;
- Superpowers code-review verdict;
- CTO verdict;
- repair history;
- unresolved non-blocking risks; and
- explicit actions required from the human.

The skill does not merge. A human reviews the report and merges the pull request into `dev`.

## Planning and Integration Tickets

Work requiring both frontend and backend changes is decomposed into:

- a backend child ticket;
- a frontend child ticket; and
- an integration ticket.

The planner must define shared contracts before parallel implementation begins. Child tickets may run concurrently only when their dependencies permit it and they use isolated worktrees.

The integration ticket verifies the combined behavior after its dependencies merge into `dev`. v0.1 may execute children sequentially; parallel dispatch is deferred until local isolation has been validated.

## Milestone Releases

Feature agents never merge directly to `main`.

When all tickets in a Linear milestone are complete, the CTO prepares a `dev` to `main` release proposal containing:

- milestone scope;
- included pull requests;
- full-system verification evidence;
- migrations;
- known risks;
- rollback notes; and
- steering or ADR changes.

A human approves and merges the milestone release pull request.

## Role Contracts

### Planner

The planner owns roadmap-to-work decomposition and ticket quality. It may read the approved roadmap, Linear context, steering documents, ADRs, and repository structure. Through the parent workflow it may create and refine draft Linear milestones, tickets, dependencies, contracts, acceptance criteria, integration work, and risks.

It may not edit code, approve its own plan, alter steering truth, move tickets to `Agent Ready`, mutate active tickets, or open and merge implementation pull requests.

### Backend implementer (Superpowers)

Backend tickets use the Superpowers SDD stock implementer. Same boundaries as any implementer: edit code, run checks, commit, prepare a PR; never merge, approve, expand scope, or edit steering.

### Frontend developer

The frontend developer is the specialized implementer for UI tickets inside the Superpowers SDD loop. It must read `docs/DESIGN.md` and relevant product screens before UI edits, follow project UI composition rules, and refuse to invent a deferred brand system.

It may edit code, run checks, commit, and prepare a pull request. It may not merge, approve, expand scope, edit steering artifacts, or silently change an agreed interface.

### Code reviewer (Superpowers)

Superpowers `requesting-code-review` judges the exact SHA. Reviewers may return findings and a formal verdict. They may not push fixes, inspect the developer transcript, redefine requirements, or merge.

### CTO

The CTO guards product scope, architecture, roadmap alignment, and durable decisions after code review.

If implementation conflicts with steering, the CTO blocks the feature and proposes a separate steering change for human approval. It may not silently reinterpret steering, patch the feature branch, or merge to `main`.

### Human

The human:

- approves generated plans;
- moves Linear work to `Agent Ready`;
- resolves ambiguity and escalations;
- approves steering changes;
- reviews merge-readiness reports;
- merges feature pull requests into `dev`; and
- approves and merges milestone releases into `main`.

## Gate Semantics

Prompt instructions are procedural safeguards, not enforcement.

Bootstrap enforcement consists of:

- protected `dev` and `main` branches;
- pull requests instead of direct pushes;
- fresh role separation;
- deterministic verification evidence;
- explicit human approval; and
- human-controlled merges.

Cursor hooks may block obvious protected-branch or merge commands, but hooks are also guardrails rather than server-side security boundaries.

Automated unattended merging requires external enforcement and is deferred.

## Error Handling

The skill fails closed for:

- missing or ambiguous acceptance criteria;
- unapproved decomposition;
- unresolved ticket dependencies;
- steering contradictions;
- missing verification commands;
- missing required Superpowers skills;
- unsafe local changes;
- unavailable required models for pinned roles;
- stale or mismatched SHAs;
- any blocking review or CTO verdict; and
- exhausted repair cycles.

The skill reports the exact blocking condition and the next human action. It must not reinterpret failure as success or remove a gate to make progress.

## Local Run Records

The ignored local record under `.agent-delivery/runs/<ticket-id>/` may contain:

- `run.md` — phase, selected models, branch, pull request, and current SHA
- `plan.md` — planner / writing-plans output and human decision
- `verification.md` — commands and results
- `code-review.md` — Superpowers review output
- `cto-review.md`
- `repairs.md`
- `merge-readiness.md`

These files must not contain credentials or raw secrets. Reports intended to survive beyond the local session should be copied into Linear or the GitHub pull request.

## Validation Strategy

### Dry-run scenarios

Validate the skills against fixtures covering:

- an approved roadmap milestone with no Linear tickets;
- an idempotent rerun that refines existing draft tickets without duplication;
- a roadmap-to-Linear conflict involving an active ticket;
- a duplicate approved roadmap identifier during a milestone-scoped run;
- a malformed milestone or deliverable declaration alongside legitimate mentions such as `### Deliverables for M1` that must not block;
- a roadmap-link diff that deletes roadmap intent, which must discard the branch and block;
- prefix-neighbour sync keys such as `M10` and `M1-D10` that must not satisfy `M1` and `M1-D1`;
- a complete milestone derived from its Linear ticket references;
- an `origin/main` divergence or fetch failure;
- an unavailable GitHub forge during the mechanical roadmap-link pull request;
- an atomic backend ticket executed through Superpowers SDD;
- a frontend ticket that dispatches `frontend-developer` rather than the stock implementer;
- a parent ticket requiring frontend and backend decomposition;
- a missing acceptance criterion;
- a failed local check;
- a blocking Superpowers review or CTO steering-drift finding;
- a repaired SHA that invalidates prior evidence; and
- exhausted repair cycles.

### First real vertical slice

The first successful slice is one Linear ticket that:

1. is created or refined from an approved roadmap milestone;
2. receives human `Agent Ready` approval;
3. is implemented through `/agent-delivery` using Superpowers SDD (stock or frontend packet as appropriate);
4. passes deterministic local checks;
5. receives Superpowers code-review approval;
6. receives CTO approval;
7. produces a complete merge-readiness report; and
8. is merged by a human into `dev`.

### Success criteria

The workflow is validated when:

- every active roadmap deliverable maps to exactly one Linear sync key;
- rerunning roadmap planning refines draft work without creating duplicates;
- active-ticket or roadmap conflicts are reported without unsafe mutation;
- every decision is traceable to the ticket, SHA, and role report;
- no agent crosses its role boundary;
- backend delivery does not depend on a custom backend-developer agent;
- frontend delivery requires the specialized frontend packet;
- a new SHA reliably invalidates old evidence;
- failures stop at the correct gate;
- a human can understand why the pull request is or is not merge-ready; and
- the process completes without a coordinator service, database, or cloud execution.

## Evolution Path

Automation is driven by observed repetition:

1. Stabilize the project skills through manual runs, keeping Superpowers as the delivery engine.
2. Extract deterministic repeated Linear/GitHub operations into local scripts or a CLI.
3. Add GitHub Actions or a self-hosted runner after verification commands stabilize.
4. Add a Linear `Agent Ready` Cursor Automation when remote execution is useful.
5. Move generic workflow assets into a delivery-platform repository when more than one product needs them.
6. Add durable PostgreSQL state, webhook handling, scoped Apps, and a credential broker only when concurrent unattended workflows require them.

Each phase must preserve the same role boundaries and gate semantics.
