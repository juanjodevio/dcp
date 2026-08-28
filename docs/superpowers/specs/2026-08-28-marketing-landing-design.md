# Marketing Landing Design

**Date:** 2026-08-28  
**Status:** Ready for review  
**Related:** `docs/PRODUCT.md`, `docs/DESIGN.md`, [DCP-29](https://linear.app/medaiec/issue/DCP-29) (M1-D4), `docs/superpowers/specs/2026-08-25-dbt-control-plane-mvp-design.md`

## Purpose

Ship a public discovery page **before** control-plane application code so an open-source adopter can understand what dcp is, that it is self-hosted (not a SaaS), and where to find the repository.

This is not Getting started, not the Next.js operator UI, and not M7 adopter documentation.

## Decisions

| Topic | Decision |
|-------|----------|
| When | M1, in parallel with DCP-12; does **not** block M2 |
| Path | `www/` at repo root (`www/index.html`, `www/styles.css`) |
| Stack | Static HTML + CSS only. No Next.js, no npm, no build step |
| Hosting | In-repo files are the M1 deliverable. GitHub Pages from `/www` is optional and may be unavailable while the repo is private |
| CTA | Primary link: `https://github.com/juanjodevio/dcp` |
| Honesty | Product is in development; do not imply a running hosted app or Compose stack that does not exist yet |
| Visual | Landing may have its own language via `design-taste-frontend`. Do not copy tokens into `control-plane/ui/` |
| Implementer | Landing skill pack in `docs/DESIGN.md`. Do **not** dispatch `frontend-developer` |

## Audience and job

- **Who:** data engineer / OSS evaluator discovering the project.
- **Job:** decide whether to star/watch/clone, not create a project or trigger a run.
- **Not for:** operators who already have Compose up (that is Getting started in the app).

## Page structure (single page)

1. **Hero** — name `dcp`; one sentence: open-source, self-hostable control plane for dbt Core with Elementary.
2. **Problem** — Cloud-like dbt ops today means vendor lock-in or ad-hoc CI/scripts.
3. **Product** — only v0.1 in-scope capabilities from `docs/PRODUCT.md`: projects, environments, jobs, schedules, runs, artifacts, lineage, Elementary, Local Docker + optional AWS Batch, Docker Compose.
4. **Constraints** — v0.1 is single-user, no auth; bind privately. dbt’s model DAG stays in dbt.
5. **Status** — control plane is being built in this repo; landing is the public face until Compose exists.
6. **CTA** — GitHub repository. No “Open app”, no signup, no fake dashboard screenshot of a product that does not exist.
7. **Footer** — GitHub link; no invented legal entity or brand lockup beyond `dcp`.

## Copy rules

- Claims must be traceable to `docs/PRODUCT.md` and the MVP spec. Do not add features (auth, multi-tenant, Helm, Temporal).
- Do not replace Elementary’s product with a fake observability story.
- Do not use SaaS pricing, waitlist, or “get started in the cloud” language.
- Required visible strings (for verification): `dcp`, `dbt Core`, `Elementary`, `Docker Compose`, `self-host`, and the GitHub URL above.

## Architecture

```text
www/
  index.html    # single page; semantic landmarks (header, main, footer)
  styles.css    # landing visual language only
```

Open locally with a static server (for example `python3 -m http.server -d www 4173`). No application process, API, or Compose dependency.

## Non-goals (this spec)

- Operator UI screens, tokens, or Next.js scaffold
- Docs site, blog, changelog UI
- Auth, analytics pixels, cookie banners
- Promoting landing visual tokens into the app (DCP-26)
- M7 Compose runbooks (landing may later link to them)

## Verification

- Required copy strings and GitHub CTA present in `www/index.html`.
- Keyboard: skip to main content; primary CTA reachable.
- Contrast readable on hero and body text (landing pack `web-design-guidelines`).
- Human: open the page locally; confirm it does not look like Getting started or a dashboard.

## Delivery

Linear deliverable **[DCP-29](https://linear.app/medaiec/issue/DCP-29)** (`M1-D4`) under M1. Depends on M1-D1 (steering copy). Does not block M1-D3 or M2.

Prefer a manual implementer session with the landing skill pack. If `/agent-delivery` is used, do not fill the implementer from `.cursor/agents/frontend-developer.md`.
