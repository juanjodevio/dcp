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

## `/agent-delivery`

May: preflight; dispatch roles per ownership table; create or refine tickets only in `Draft` or `Needs Planning` (including child tickets from planner decomposition), via the parent workflow; write Linear status notes; set ticket to `Blocked — Human` when repair cycles are exhausted (or report that state when Linear mutation is unavailable); maintain run records.

May not: move tickets to `Agent Ready`; delete/cancel/close/downgrade tickets; mutate `Agent Ready` or other active/terminal tickets' scope; invent verification or delivery success; merge; edit steering.

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
