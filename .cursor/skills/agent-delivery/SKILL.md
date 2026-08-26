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
- required pinned model is unavailable (CTO `gpt-5.6-sol`);
- workspace is unsafe and isolation cannot be established;
- review or CTO blocks;
- repair cycles are exhausted (max 2).

Never merge. Never edit steering to unblock a ticket. Never invent verification success.

## Linear writes (live only)

Permitted: create or refine tickets only in `Draft` or `Needs Planning` (including child tickets from planner decomposition), via the parent workflow; write Linear status notes; when repair cycles are exhausted, write a status note and apply label `blocked-human` (or report that action when Linear mutation is unavailable).

Forbidden: move to `Agent Ready`; delete/cancel/close/downgrade tickets; mutate `Agent Ready` or other active/terminal tickets' scope; invent success; invent a dedicated Blocked workflow state.

## Preflight

1. Load `AGENTS.md` and relevant steering docs.
2. Fetch the Linear ticket and approved descendants.
3. Confirm state is `Needs Planning` or `Agent Ready`.
4. Check unresolved dependencies.
5. Classify ticket as `frontend`, `backend`, or `integration`.
6. Confirm verification entrypoint exists in `AGENTS.md`.
7. Confirm Superpowers skills are available: `subagent-driven-development`, `requesting-code-review`, `finishing-a-development-branch`, and `using-git-worktrees` / `writing-plans` when needed.
8. Confirm required pinned models are available (CTO: `gpt-5.6-sol`); record resolved role-model configuration in `run.md`.
9. Identify `dev` base SHA.
10. Create or resume `.agent-delivery/runs/<ticket-id>/run.md`.

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
9. On any blocking verification, review, or CTO verdict, run the repair loop (same implementer path as the ticket). Each new SHA invalidates prior evidence. After two unsuccessful repairs, write a status note, apply label `blocked-human`, and stop.
10. When gates pass, invoke Superpowers `finishing-a-development-branch` for PR options toward `dev`, write the Merge Readiness Report, and leave merge to a human.
11. Write Linear status notes per permitted writes above.
