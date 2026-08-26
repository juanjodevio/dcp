# Design

Status: Draft
Last Reviewed: 2026-08-25

## Context

dcp needs a clear operator UI for an open-source, single-user control plane: projects, environments, jobs, schedules, runs (logs/artifacts/Elementary), lineage, and settings. The first visit with zero projects must show a **Getting started** flow rather than an empty table.

Product surfaces are defined in `docs/PRODUCT.md` and `docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md`. There is no existing UI codebase or brand system yet.

## Proposed Solution

### Screens (v0.1)

1. Getting started — empty state when there are no projects; guided project → environment → job
2. Projects list + create
3. Project detail — environments, jobs, schedules
4. Job detail — trigger run, schedule editor
5. Runs list + run detail — split `dbt_status` / `observability_status`, logs, artifacts, Elementary summary, retry/cancel/rerun
6. Lineage view — project-scoped graph from normalized edges
7. Settings — runner defaults, AWS Batch config presence, Elementary config

### UI principles (interim)

- One primary job per screen; Getting started is the onboarding composition, not a dashboard collage
- Run detail prioritizes status, logs, and artifacts over secondary chrome
- Make dbt vs observability failure distinguishable in the UI (split statuses)
- Prefer progressive disclosure for Advanced runner/AWS settings

### Visual system

Not yet defined. Do not invent a default AI aesthetic. Establish tokens, typography, and layout direction in a follow-up design pass or ADR before polishing the UI beyond usable MVP chrome.

### Frontend agent skills (install before first UI ticket)

Defer Impeccable until the first real UI ticket (it wants `/impeccable init` against a live design context):

```bash
npx impeccable install
# then in Cursor: /impeccable init
```

Install these for the `frontend-developer` packet whenever ready:

```bash
npx skills add https://github.com/vercel-labs/agent-skills --skill vercel-composition-patterns
npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines
npx skills add https://github.com/vercel-labs/agent-skills --skill react-best-practices
```

### Accessibility

Expectation for v0.1: keyboard-reachable primary flows and readable contrast on run logs/status. Full WCAG target level is **Unknown**.

## Consequences

- Positive: agents and humans share a fixed screen list for MVP UI work
- Positive: Getting started is an explicit product requirement, not an afterthought
- Trade-off: visual brand is deferred; early UI may look utilitarian until a design system lands

## Stitch Compatibility

`docs/DESIGN.md` is canonical. If another location needs `DESIGN.md`, prefer a symlink to this file. Use a copy only when symlinks are not practical and record why.

## Assumptions

- Next.js is the UI framework (`docs/TECH.md`)
- Single-user means no login/account chrome in v0.1

## Unknowns

- Brand name display treatment beyond “dcp”
- Color, type, motion, and component library choices
- Accessibility compliance level (e.g. WCAG 2.2 AA) for public release
