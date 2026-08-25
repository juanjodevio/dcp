# Local-First Agent Delivery Workflow

**Date:** 2026-08-25  
**Status:** Approved

## Purpose

Validate an agent-driven software delivery workflow without first building an orchestration platform.

The initial system uses two project-local Cursor skills invoked manually:

```text
/plan-roadmap
/agent-delivery LINEAR-ID
```

`/plan-roadmap` turns the approved roadmap into milestones and draft Linear work. `/agent-delivery` coordinates fresh ticket refinement, implementation, review, and technical-governance agents. Humans approve roadmap changes, move tickets to `Agent Ready`, resolve ambiguity, and merge pull requests. Automation is added only after repeated manual runs reveal stable transitions worth automating.

## Decisions

- Linear is the canonical source for work scope, acceptance criteria, dependencies, and status.
- GitHub is the canonical Git forge, pull-request system, and merge record.
- Product steering documents and ADRs are the canonical sources for durable product and technical direction.
- The version of `docs/ROADMAP.md` merged into `main` authorizes the Planner to create and refine corresponding draft Linear work without a second planning approval.
- Roadmap authority is resolved by mode. While no `origin` remote exists, the committed local `main` branch is the approved authority in `local-main-bootstrap` mode. Once an `origin` remote exists, authority is `origin-main`: fetch `origin/main`, require local `main` to equal it, and fail closed on divergence or fetch failure. Every report records the authority mode and the resolved roadmap SHA.
- Roadmap milestone activity is derived from the Linear ticket references recorded in the approved roadmap, not from roadmap prose.
- After creating tickets, the roadmap planning workflow opens a mechanical roadmap-link pull request targeting `main` for human merge. It adds only Linear ticket reference lines and never commits to `main`.
- The first version runs locally in Cursor and is started manually.
- The workflows live in `.cursor/skills/plan-roadmap/` and `.cursor/skills/agent-delivery/` in the product repository.
- Feature branches target `dev`. Milestone release pull requests and mechanical roadmap-link pull requests target `main`.
- Humans merge into both `dev` and `main` during the bootstrap phase.
- Planner and developer models are configurable by role.
- Reviewer A uses GPT-5.6 Sol.
- Reviewer B uses Claude Opus 5.
- The CTO reviewer uses GPT-5.6 Sol.
- Every role invocation is a fresh, bounded run.
- Two unsuccessful repair cycles stop the workflow for human intervention.

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
- Fresh frontend or backend implementation agent
- Local deterministic verification
- Two independent code-review agents
- CTO scope and steering-drift review
- At most two repair cycles
- Merge-readiness reporting
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

### Non-goals

- Treating prompts as security boundaries
- Letting agents redefine ticket scope
- Letting implementation agents edit steering documents
- Letting reviewers patch code they review
- Replacing Linear or GitHub with a custom task or pull-request system
- Building a general autonomous-company control plane

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
- a root `AGENTS.md` that points agents to those documents and contains a `## Delivery Workflow` section with `Linear team: <team-key>`;
- `dev` and `main` branches with direct pushes blocked;
- a GitHub remote and authenticated `gh` CLI. Until this exists, roadmap planning runs in `local-main-bootstrap` authority mode and reports its mechanical roadmap-link pull request as PARTIAL or BLOCKED with the exact setup action rather than committing to `main`;
- Linear states named `Needs Planning`, `Agent Ready`, and `Blocked — Human`;
- one verification command documented in `AGENTS.md`; and
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
  backend-developer.md
  reviewer-a.md
  reviewer-b.md
  cto.md
```

`SKILL.md` is explicit-only and uses `disable-model-invocation: true`. It defines the state machine, hard stops, repair limit, context assembly, and handoffs.

`ROLE-CONTRACTS.md` defines each role's inputs, outputs, allowed actions, and prohibited actions.

`REPORT-TEMPLATES.md` defines planner, implementation, verification, review, CTO, repair, and merge-readiness outputs.

`MILESTONE-TEMPLATES.md` defines roadmap authoring forms, required parsing patterns, sync-key exactness, milestone activity derivation, and the roadmap coverage, milestone plan, Linear ticket, dependency, and reconciliation outputs.

`DRY-RUN-SCENARIOS.md` defines the named roadmap planning fixtures. Its second-level headings are the complete set of valid scenario names, and an unknown name lists the valid names and stops.

The optional project subagent files provide stable named roles. Planner and review roles are declared read-only. Reviewer and CTO files pin their approved models; planner and developer files inherit the selected parent model so they remain configurable. Each skill remains the workflow coordinator and invokes roles explicitly.

A `readonly: true` frontmatter value is a declaration inside a prompt asset, not an enforcement boundary. Whether Cursor actually restricts a discovered subagent's tools must be verified in the product, and that verification is a human acceptance item.

No executable helper scripts are required initially. Stable repeated operations may be extracted after the workflow has been exercised.

## Roadmap Planning Workflow

`/plan-roadmap` resolves roadmap authority, reads the approved `docs/ROADMAP.md` from `main` at that authority commit, then compares every active milestone with existing Linear projects, milestones, and tickets.

Milestone activity is derived from the `Linear tickets:` references recorded in each approved milestone section. A milestone with no references, or with any referenced ticket in a nonterminal state, is active. A milestone whose every referenced ticket is completed is complete, and the workflow generates no fresh drafts for it. A canceled, unresolvable, or contradicting reference needs human reconciliation and also produces no fresh drafts.

The Planner:

1. turns roadmap outcomes into dependency-ordered deliverables;
2. identifies backend, frontend, integration, migration, documentation, and operational work;
3. defines acceptance criteria, contracts, verification requirements, risks, and milestone dependencies;
4. proposes missing Linear tickets in `Draft` or `Needs Planning`;
5. proposes refinements to existing tickets only while they remain in `Draft` or `Needs Planning`;
6. assigns every ticket a stable roadmap sync key matched only by full-value equality, so `M1` never matches `M10` and `M1-D1` never matches `M1-D10`; and
7. reports coverage gaps, stale tickets, conflicts, and milestone drift.

The parent workflow, not the Planner, applies the permitted Linear mutations and owns the Reconciliation Report.

The approved roadmap is sufficient authorization for these draft mutations. The workflow does not require a second human approval before creating or refining draft tickets.

Planner may not:

- change `ROADMAP.md` or product intent;
- move any ticket to `Agent Ready`;
- rewrite tickets already in `Agent Ready` or an active delivery state;
- delete, cancel, or close work;
- resolve roadmap contradictions by assumption; or
- implement code.

Duplicate roadmap keys, duplicate Linear sync keys, unproven roadmap authority, and unproven search scope or pagination fail closed on every run, including a run scoped to a single milestone. Stale detection is always global.

After a live run creates tickets, the workflow opens one mechanical roadmap-link pull request from a dedicated branch into `main`. It may add only `Linear tickets:` reference lines, must never change roadmap intent, and is merged by a human. When GitHub is unavailable, the branch stays local and unmerged and the run reports PARTIAL or BLOCKED with the exact setup action.

Conflicts between the approved roadmap and current Linear state produce a reconciliation report for a human. The workflow is idempotent: rerunning it updates matching draft work instead of creating duplicates.

## Ticket Invocation and Status Rules

The command is valid for two Linear states.

### `Needs Planning`

The skill:

1. Reads the parent ticket, steering documents, ADRs, and repository structure.
2. Launches a fresh planner.
3. Produces a proposed decomposition containing child tickets, dependencies, interfaces, integration checks, risks, and acceptance criteria.
4. Publishes or presents the proposal.
5. Stops.

The planner may create or refine child tickets in `Draft` or `Needs Planning`. It cannot mark its own plan ready. A human reviews the resulting ticket set and moves eligible work to `Agent Ready`.

### `Agent Ready`

The skill verifies that the ticket is either:

- atomic, with explicit acceptance criteria, interfaces, and verification steps; or
- backed by a human-approved child-ticket plan.

If neither condition holds, the skill fails closed and requests planning. Otherwise, it proceeds with implementation.

## Delivery Flow

### 1. Preflight

The skill:

- loads `AGENTS.md` and relevant steering documents;
- retrieves the Linear ticket and approved descendants;
- confirms the ticket is eligible to run;
- checks for unresolved dependencies;
- identifies the frontend or backend role;
- confirms a deterministic verification entrypoint exists;
- records the selected role-model configuration;
- identifies the `dev` base SHA; and
- creates or resumes the local run record.

Missing intent, conflicting steering, a missing verification command, or an unclean unsafe workspace blocks execution.

### 2. Isolated implementation

The skill creates a feature branch from the current `dev` branch. The expected naming convention is:

```text
feat/<linear-id>-<short-slug>
```

The developer receives only:

- the approved ticket and relevant ancestors;
- acceptance criteria;
- relevant steering and ADR excerpts;
- dependency contracts;
- repository instructions;
- relevant code context; and
- required verification commands.

The developer implements one approved work item, runs local checks, commits the result, and prepares a pull request. The developer cannot merge, approve, expand scope, or edit steering artifacts.

### 3. Deterministic verification

The skill runs the repository's versioned verification entrypoint against the exact feature-branch SHA.

The entrypoint should eventually cover formatting, linting, static types, unit tests, and relevant integration tests. Until the product repository defines that entrypoint, delivery must stop rather than inventing an unverifiable success claim.

Verification evidence records:

- command;
- start and completion time;
- exit status;
- tested SHA; and
- concise failure output or success summary.

### 4. Independent reviews

After deterministic checks pass, the skill launches three fresh review runs.

Reviewer A and Reviewer B receive:

- the approved ticket and acceptance criteria;
- the exact diff and head SHA;
- verification evidence;
- relevant steering documents and ADRs; and
- repository instructions.

They do not receive the developer transcript or each other's findings. Each returns a structured `approve` or `changes_requested` verdict with findings tied to files and evidence.

During local bootstrap, these verdicts are role-labeled reports posted by the parent workflow under the human's GitHub identity. They are not independent GitHub-account approvals. Distinct enforceable reviewer identities are deferred.

The CTO reviewer receives ticket ancestry, scope, the diff, the head SHA, steering documents, ADRs, verification evidence, and both reviewer reports. The CTO evaluates:

- scope drift;
- contradictions with product direction;
- architectural drift;
- missing durable decisions;
- inappropriate steering changes; and
- milestone or roadmap impact.

The CTO does not perform a third general code review.

### 5. Repair loop

Any failed deterministic check or `changes_requested` verdict blocks merge readiness.

The skill launches a fresh repair agent with:

- the approved ticket;
- the current diff and SHA;
- failing verification evidence;
- all blocking findings; and
- relevant repository guidance.

A pushed repair creates a new SHA. All previous checks and reviews become stale and must run again.

Two unsuccessful repair cycles result in `Blocked — Human`. Transient tool or infrastructure failures may be retried and do not count as repair cycles unless they produce a code change.

### 6. Merge readiness

When all gates pass, the skill produces a merge-readiness report containing:

- Linear ticket and approved plan;
- branch, pull-request link, and exact SHA;
- verification evidence;
- Reviewer A verdict;
- Reviewer B verdict;
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

Feature agents never merge directly to `main`. No agent commits or pushes to `main`; the mechanical roadmap-link pull request is the only agent-authored change targeting `main`, and a human merges it.

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

### Frontend and backend developers

Each developer implements one approved child ticket on an isolated branch. The role may edit code, run checks, commit, and prepare a pull request.

It may not merge, approve, expand scope, edit steering artifacts, or silently change an agreed interface.

### Reviewer A and Reviewer B

Reviewers independently judge the same exact SHA. They may return findings and a formal verdict.

They may not push fixes, inspect the developer transcript, dismiss the other review, redefine requirements, or merge.

### CTO

The CTO guards product scope, architecture, roadmap alignment, and durable decisions.

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

- unproven roadmap authority, including a failed `origin/main` fetch or a local `main` that diverges from `origin/main`;
- duplicate approved roadmap identifiers or duplicate Linear sync keys;
- a Linear issue description with zero or more than one `Roadmap sync key:` line;
- a malformed milestone argument or a milestone argument absent from the approved roadmap;
- an unknown dry-run scenario name;
- missing or ambiguous acceptance criteria;
- unapproved decomposition;
- unresolved ticket dependencies;
- steering contradictions;
- missing verification commands;
- unsafe local changes;
- unavailable required reviewer models;
- stale or mismatched SHAs;
- any blocking review verdict; and
- exhausted repair cycles.

The skill reports the exact blocking condition and the next human action. It must not reinterpret failure as success or remove a gate to make progress.

## Local Run Records

The ignored local record under `.agent-delivery/runs/<ticket-id>/` may contain:

- `run.md` — phase, selected models, branch, pull request, and current SHA
- `plan.md` — planner output and human decision
- `verification.md` — commands and results
- `review-a.md`
- `review-b.md`
- `cto-review.md`
- `repairs.md`
- `merge-readiness.md`

These files must not contain credentials or raw secrets. Reports intended to survive beyond the local session should be copied into Linear or the GitHub pull request.

## Validation Strategy

### Dry-run scenarios

Validate the skill against fixtures covering:

- an approved roadmap milestone with no Linear tickets;
- an idempotent rerun that refines existing draft tickets without duplication;
- a roadmap-to-Linear conflict involving an active ticket;
- a duplicate approved roadmap identifier during a milestone-scoped run;
- prefix-neighbour sync keys such as `M10` and `M1-D10` that must not satisfy `M1` and `M1-D1`;
- a complete milestone derived from its Linear ticket references;
- an `origin/main` divergence or fetch failure;
- an unavailable GitHub forge during the mechanical roadmap-link pull request;
- an atomic backend ticket;
- a parent ticket requiring frontend and backend decomposition;
- a missing acceptance criterion;
- a failed local check;
- conflicting reviewer verdicts;
- steering drift detected by the CTO;
- a repaired SHA that invalidates prior evidence; and
- exhausted repair cycles.

### First real vertical slice

The first successful slice is one Linear ticket that:

1. is created or refined from an approved roadmap milestone;
2. receives human `Agent Ready` approval;
3. is implemented by one fresh local developer agent;
4. passes deterministic local checks;
5. receives independent approval from Reviewer A and Reviewer B;
6. receives CTO approval;
7. produces a complete merge-readiness report; and
8. is merged by a human into `dev`.

### Success criteria

The workflow is validated when:

- every active roadmap deliverable maps to exactly one Linear sync key;
- sync keys are matched only by full-value equality, so prefix neighbours never collide;
- rerunning roadmap planning refines draft work without creating duplicates;
- active-ticket or roadmap conflicts are reported without unsafe mutation;
- roadmap authority mode and the resolved roadmap SHA appear in every report;
- the mechanical roadmap-link pull request is opened for human merge and never merged by an agent;
- every decision is traceable to the ticket, SHA, and role report;
- no agent crosses its role boundary;
- a new SHA reliably invalidates old evidence;
- failures stop at the correct gate;
- a human can understand why the pull request is or is not merge-ready; and
- the process completes without a coordinator service, database, or cloud execution.

## Evolution Path

Automation is driven by observed repetition:

1. Stabilize the project skill through manual runs.
2. Extract deterministic repeated operations into local scripts or a CLI.
3. Add GitHub Actions or a self-hosted runner after verification commands stabilize.
4. Add a Linear `Agent Ready` Cursor Automation when remote execution is useful.
5. Move generic workflow assets into a delivery-platform repository when more than one product needs them.
6. Add durable PostgreSQL state, webhook handling, scoped Apps, and a credential broker only when concurrent unattended workflows require them.

Each phase must preserve the same role boundaries and gate semantics.
