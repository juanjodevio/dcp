# Design

Status: Draft
Last Reviewed: 2026-08-28

## Context

dcp needs a clear operator UI for an open-source, single-user control plane: projects, environments, jobs, schedules, runs (logs/artifacts/Elementary), lineage, and settings. The first visit with zero projects must show a **Getting started** flow rather than an empty table.

A public **marketing landing page** lives at `www/` (static HTML + CSS). Spec: `docs/superpowers/specs/2026-08-28-marketing-landing-design.md`. It is not an MVP control-plane screen and must not live in `control-plane/ui/`.

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

**Operator UI:** not yet defined. Do not invent a default AI aesthetic for product screens. Establish tokens, typography, and layout direction in a follow-up design pass or ADR (see DCP-26) before polishing the app beyond usable MVP chrome.

**Marketing landing:** own visual language under `www/`, generated with `design-taste-frontend`. Do not copy those tokens into the operator UI unless a later design pass explicitly promotes them. Do not replace this file with a third-party Stitch `DESIGN.md`.

### Frontend agent skills

One implementer: project `frontend-developer` for operator UI **and** marketing landing. Two skill packs. Do not install the full [taste-skill](https://github.com/Leonxlnx/taste-skill) repo (it pulls imagegen, brutalist, brandkit, and other variants). Pin `--skill` names. [awesome-design-md](https://github.com/voltagent/awesome-design-md) is a reference library, not an installable skill, and must not overwrite this file.

#### Marketing landing (pre-product)

Use when `frontend-developer` is building `www/`. taste-skill v2 is for landings, not dashboards. Spec: `docs/superpowers/specs/2026-08-28-marketing-landing-design.md`. Plan: `docs/superpowers/plans/2026-08-28-marketing-landing.md`.

```bash
npx skills add https://github.com/Leonxlnx/taste-skill --skill design-taste-frontend
npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines
npm install -g agent-browser && agent-browser install
```

Optional: read one operator-adjacent analog from awesome-design-md (Linear, HashiCorp, Vercel) as a vibe reference. Do not paste it in as this document.

#### Operator UI (`frontend-developer` packet)

Install before the first product UI ticket (DCP-17). Scope `react-best-practices` to waterfall and bundle rules in v0.1.

```bash
npx skills add https://github.com/vercel-labs/agent-skills --skill vercel-composition-patterns
npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines
npx skills add https://github.com/vercel-labs/agent-skills --skill react-best-practices
```

Defer Impeccable until a live product UI exists (it wants `/impeccable init` against a design context):

```bash
npx impeccable install
# then in Cursor: /impeccable init
```

`frontend-developer` implements both surfaces. Load the landing pack for `www/` and the operator pack for `control-plane/ui/`. Do not apply `design-taste-frontend` to operator screens.

### Accessibility

Expectation for v0.1: keyboard-reachable primary flows and readable contrast on run logs/status. Full WCAG target level is **Unknown**.

## Consequences

- Positive: agents and humans share a fixed screen list for MVP UI work
- Positive: Getting started is an explicit product requirement, not an afterthought
- Positive: landing vs operator UI use different skill packs, so taste-skill cannot restyle product screens by default
- Trade-off: operator visual brand is deferred; early app UI may look utilitarian until a design system lands
- Trade-off: landing visual language is independent of the operator UI until DCP-26

## Stitch Compatibility

`docs/DESIGN.md` is canonical. If another location needs `DESIGN.md`, prefer a symlink to this file. Use a copy only when symlinks are not practical and record why.

## Assumptions

- Next.js is the operator UI framework (`docs/TECH.md`)
- Single-user means no login/account chrome in v0.1
- Marketing landing is M1-D4, ships from `www/`, and does not block M2

## Unknowns

- Brand name display treatment beyond “dcp”
- Color, type, motion, and component library choices for the operator UI
- Accessibility compliance level (e.g. WCAG 2.2 AA) for public release
- Whether GitHub Pages is enabled for the private repo
- Whether landing visual language is later promoted into the operator UI (DCP-26)
