# Repo CI and Automerge Setup Design

**Date:** 2026-08-31  
**Status:** Ready for review  
**Related:** `docs/TECH.md`, `docs/STRUCTURE.md`, `AGENTS.md`, [ADR-0007](../../adr/0007-python-package-manager-uv.md), `docs/superpowers/specs/2026-08-25-agent-delivery-workflow-design.md`, `docs/superpowers/specs/2026-08-28-marketing-landing-design.md`

## Purpose

Stand up repository merge gates and toolchains so Cursor Cloud `/agent-delivery` can open feature PRs into `dev` and land when deterministic CI is green and a **human has armed auto-merge**—without requiring human *approving reviews* on that path. Milestone releases (`dev` → `main`) stay human-merged.

## Decisions

| Topic | Decision |
|-------|----------|
| Approach | Named GitHub Actions jobs + repository **rulesets** (not classic branch protection alone; no merge queue) |
| Automerge scope | Feature → `dev` only |
| `dev` → `main` | Human merge; no auto-merge |
| Required checks on `dev`/`main` | Exactly `python` and `typescript` |
| Human approving review on `dev` | Not required |
| Merge method (feature → `dev`) | Squash |
| Auto-merge arming | **Human** enables auto-merge on the PR (repo `allow_auto_merge` + rulesets are human-configured once; agents do not arm merge) |
| Python | `uv` + Ruff (lint + format) + mypy + pytest |
| TypeScript | `pnpm` + ESLint + Prettier + `tsc` + Vitest |
| Landing contract tests | Migrate from Python unittest to **Vitest under `www/`**; delete `tests/www/test_landing_copy.py` once green |
| AI PR review | **Deferred**; preferred future hard gate: **CodeRabbit** (`coderabbitai` check). No OpenAI/Codex API key in Actions for review |
| Primary delivery path | Cursor Cloud agent-delivery targeting `dev` |

## Branch policy and rulesets

### Branches

- `dev` — integration branch; all feature work merges here.
- `main` — release / milestone landings only.

### Rulesets (configure via `gh`; treat as durable ops)

**Both `dev` and `main`:**

- Require a pull request; block direct pushes.
- Block force-pushes for normal roles.
- Require status checks `python` and `typescript` to pass before merge.
- Prefer no bypass for non-admin actors; admin break-glass only if the platform requires an bypass actor.

**`dev` only:**

- Allow repository auto-merge.
- Allow squash merge as the default path for feature PRs.
- Do not require approving reviews.

**`main` only:**

- Do not enable auto-merge for release PRs.
- Human merges `dev` → `main` after release judgment.

### Repo settings

- Enable `allow_auto_merge` on the repository (required for native auto-merge).
- Do not enable a merge queue in this milestone (avoids Cursor Cloud / auto-merge friction).

### Required check name contract

Job `name:` values in Actions must match ruleset required contexts exactly: `python`, `typescript`. Renaming a job requires a simultaneous ruleset update or merges stall.

## Toolchains and layout

### Python (`uv`)

- Add root `pyproject.toml` + `uv.lock`.
- Dev/tooling: Ruff, mypy, pytest.
- Prepare package paths for planned `control-plane/` (minimal placeholder acceptable so mypy/pytest have a target).
- Ruff owns lint and format (no Black/isort).
- Stable commands (also land in `docs/TECH.md` as verified after first green run):

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
```

### TypeScript (`pnpm`)

- Lock **pnpm** as the Node package manager (update `docs/TECH.md`; add a short ADR superseding the prior “Unknown” if needed for parity with ADR-0007).
- pnpm workspace including:
  - `control-plane/ui/` — minimal Next-ready or plain TS package with smoke module + Vitest smoke test (real files so CI is not vacuously empty).
  - `www/` — small package that owns **landing copy/CTA/asset contract** Vitest tests reading `www/index.html` and `www/styles.css`. The public landing remains static HTML/CSS (no Next.js build for the page itself); Node tooling here is for tests and CI only and does not change the marketing-landing product stack.
- Stable commands:

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm format:check
pnpm typecheck
pnpm test
```

Exact script names may be workspace-filtered (`pnpm --filter www test`, etc.) but CI and `TECH.md` must document one canonical invocation set.

### Landing test migration

- Port assertions from `tests/www/test_landing_copy.py` (required strings, banned phrases, primary CTA href, styles linked) to Vitest under `www/`.
- Remove the Python landing unittest and stop documenting `python3 -m unittest tests/www/test_landing_copy.py` as the verification entrypoint.
- New `/agent-delivery` verification entrypoint: the locked landing Vitest command (plus document that full CI parity is `python` + `typescript` job steps).

## GitHub Actions

- Workflow(s) under `.github/workflows/` on `pull_request` and `push` to `dev` and `main`.
- Job **`python`:** setup uv → sync from lockfile → Ruff check → Ruff format `--check` → mypy → pytest.
- Job **`typescript`:** setup Node + pnpm → frozen install → lint → format check → `tsc` → Vitest (workspace: UI smoke + `www` landing).
- Jobs **always run** (no path filters that leave required checks skipped).
- Determinism: committed lockfiles; pin Actions to SHAs or stable version tags; tests offline; prefer `TZ=UTC` where time matters.
- No AI-review job in this milestone.

## Deferred AI PR review

### Not in this milestone

- CodeRabbit / Codex as a required merge gate.
- OpenAI or vendor API secrets in Actions for PR review.
- Custom “wait for AI review” workflows.
- `/agent-delivery` finish waiting on AI review.

### Radar (future)

- **Preferred hard gate:** CodeRabbit GitHub App posting a `coderabbitai` (or documented) status check; then add that context to the `dev` ruleset; configure `.coderabbit.yaml`; keep lint/format/types in CI.
- **Optional advisory:** Codex Automatic reviews + `## Code Review Rules` in `AGENTS.md` (quality, steering drift, security). Official Codex GitHub review is Codex-cloud triggered (`@codex review` / automatic reviews), not a first-class Actions `needs:` job, and does not replace branch protection by itself ([Codex GitHub docs](https://learn.chatgpt.com/docs/third-party/github)).

## Test policy

### Principles

- Test behavior and product contracts that can break; do not bloat with impossible or speculative scenarios.
- Leave mechanical quality to Ruff, mypy, ESLint, Prettier, and `tsc`.
- Deterministic: no network in unit tests; fixtures on disk.

### This milestone

- `www` Vitest: landing copy/CTA/asset contract (the real product test today).
- Python: minimal smoke so pytest/mypy targets exist until domain code lands.
- `control-plane/ui`: minimal Vitest smoke.

### Later (when `control-plane/core/` exists; not this PR)

- Unit-test domain rules and artifact parsing with small fixtures.
- Edge cases only where production code branches (invalid input, missing fields, idempotency, status boundaries).
- Do not unit-test frameworks or “impossible” environment failures.

## Cursor Cloud agent-delivery

Primary path: Cloud agent runs `/agent-delivery`, pushes a feature branch, and opens a **ready-for-review** PR into `dev`. A **human** then arms auto-merge on that PR (UI or `gh pr merge --auto --squash`). GitHub merges when `python` and `typescript` are green.

### Constraints

- Feature branches are unprotected; only `dev`/`main` use rulesets.
- Connected GitHub identity for Cloud needs write: push branch and open PR. Enabling auto-merge is a **human** action (write access on the human account).
- Do not require human *approving reviews*, CODEOWNERS approval, or signed commits in this milestone unless Cloud’s GitHub identity is proven to satisfy them. Human arming auto-merge is not the same as an approving review.
- Cloud and CI share the same install/test commands from `TECH.md`.
- Finish does **not** wait on deferred AI review and does **not** enable auto-merge.
- Cloud agents target **`dev` only**; they do not merge to `main`.

### Human arming step

After the agent opens (or updates) the PR:

1. Confirm the PR is ready for review (not draft).
2. Enable auto-merge with squash (GitHub UI or `gh pr merge --auto --squash`).
3. If checks are already green, GitHub may merge immediately; otherwise the PR stays armed until `python` and `typescript` pass.

## Steering updates (same change set as implementation)

- `docs/TECH.md` — lock uv + pnpm; verified commands; new verification entrypoint.
- `docs/STRUCTURE.md` — `.github/` CI; `www` as pnpm package for tests; test layout.
- `AGENTS.md` — point at new verification commands only (do not duplicate full policy).
- Add a short ADR locking pnpm (parity with ADR-0007 for uv) and update the ADR index; mirror the lock in `docs/TECH.md`.
- Agent-delivery skill / finish notes: open ready-for-review PR into `dev`; do **not** arm auto-merge (human does); no AI-review wait.

## Non-goals

- Merge queue.
- Required human approval on feature → `dev`.
- Automerge to `main`.
- AI PR review as a merge gate.
- Scaffolding full FastAPI/Next.js product beyond minimal placeholders needed for green CI.
- Path-filtered CI that skips required jobs.
- `/agent-delivery` (or other automation) enabling auto-merge on PRs.

## Failure modes

| Failure | Handling |
|---------|----------|
| Required check name mismatch | Treat job names as a contract; update ruleset with the rename |
| Missing/out-of-date lockfile | CI fails closed |
| Draft PR left draft | Auto-merge never runs; agent or human must mark ready for review before arming |
| Auto-merge disabled on repo | Human cannot arm; enable `allow_auto_merge` once |
| Human never arms auto-merge | PR stays open even when CI is green |
| Red CI | PR does not merge; agent repair cycle / human intervention |

## Success criteria

1. Feature PR into `dev` with green `python` + `typescript` squash-merges via auto-merge after a **human arms** it, without a human approving review.
2. Direct pushes to `dev`/`main` are blocked by rulesets.
3. `dev` → `main` still requires a human merge.
4. Landing contract is enforced by Vitest under `www/`; old Python landing unittest is gone.
5. `TECH.md` / `AGENTS.md` document commands that match CI.
6. No AI-review secret or required AI check is introduced.
7. `/agent-delivery` opens ready-for-review PRs into `dev` and does not itself enable auto-merge; humans can arm auto-merge against this repo configuration.
