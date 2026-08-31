# Repo CI and Automerge Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap uv/pnpm toolchains, deterministic GitHub Actions (`python` + `typescript`), migrate landing contract tests to Vitest under `www/`, update steering, and document human-configured rulesets/auto-merge for feature → `dev`.

**Architecture:** Root `uv` Python project with a minimal `src/dcp` package for smoke/typecheck targets; pnpm workspace with `www` (landing Vitest only) and `control-plane/ui` (TS smoke). One CI workflow with jobs named exactly `python` and `typescript`. Repo rulesets and `allow_auto_merge` are applied via `gh` as a final human ops task. Agents open PRs; humans arm auto-merge.

**Tech Stack:** Python 3.12, uv, Ruff, mypy, pytest; Node 22, pnpm 9, TypeScript 5.x, ESLint, Prettier, Vitest; GitHub Actions; GitHub repository rulesets.

## Global Constraints

- Required check job names must be exactly `python` and `typescript`.
- Feature → `dev` only for auto-merge; `dev` → `main` stays human merge; no merge queue.
- No required human *approving* review on `dev`; human **arms** auto-merge (agents must not run `gh pr merge --auto`).
- Landing page stays static HTML/CSS; `www/package.json` is tests/CI only.
- No AI PR review gate, no review API secrets in Actions; CodeRabbit is deferred (radar only).
- CI jobs always run (no path filters that skip required checks).
- Lockfiles committed; tests offline; prefer `TZ=UTC` in CI.
- Verification entrypoint becomes the locked `www` Vitest command in `AGENTS.md` / `TECH.md`.
- Do not scaffold full FastAPI/Next.js product beyond minimal placeholders.
- Spec authority: `docs/superpowers/specs/2026-08-31-repo-ci-automerge-setup-design.md`.

## File map

| Path | Responsibility |
|------|----------------|
| `pyproject.toml`, `uv.lock` | Python project + Ruff/mypy/pytest config |
| `src/dcp/__init__.py` | Minimal importable package |
| `tests/test_smoke.py` | Python smoke test |
| `pnpm-workspace.yaml`, root `package.json` | Workspace scripts |
| `www/package.json`, `www/vitest.config.ts`, `www/tsconfig.json`, `www/tests/landing-copy.test.ts` | Landing contract Vitest |
| `control-plane/ui/package.json`, `control-plane/ui/src/smoke.ts`, `control-plane/ui/src/smoke.test.ts`, TS/ESLint/Prettier configs | UI smoke package |
| `.github/workflows/ci.yml` | Jobs `python` and `typescript` |
| `docs/adr/0008-node-package-manager-pnpm.md`, `docs/adr/index.md`, `docs/adr/0007-…` (consequence tweak) | Lock pnpm |
| `docs/TECH.md`, `docs/STRUCTURE.md`, `AGENTS.md` | Commands and layout truth |
| `.cursor/skills/agent-delivery/SKILL.md` | Finish: no auto-merge arming; verification entrypoint |

---

### Task 1: Python uv bootstrap and smoke test

**Files:**
- Create: `pyproject.toml`
- Create: `src/dcp/__init__.py`
- Create: `tests/test_smoke.py`
- Create: `uv.lock` (via `uv lock` / `uv sync`)
- Modify: `.gitignore` (add `.venv/`, `node_modules/`, coverage artifacts if missing)
- Delete later (Task 2): `tests/www/test_landing_copy.py` — do **not** delete in this task

**Interfaces:**
- Consumes: nothing
- Produces: package `dcp` with `__version__ = "0.0.0"`; pytest module `tests/test_smoke.py::test_package_version`

- [ ] **Step 1: Write the failing smoke test**

Create `tests/test_smoke.py`:

```python
from dcp import __version__


def test_package_version() -> None:
    assert __version__ == "0.0.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -c "import dcp"` or `pytest tests/test_smoke.py -v` if pytest already available.

Expected: FAIL / `ModuleNotFoundError: No module named 'dcp'` (or pytest not installed yet — that is also a fail-before-bootstrap signal).

- [ ] **Step 3: Add `pyproject.toml` and package**

Create `src/dcp/__init__.py`:

```python
"""Minimal dcp package placeholder until control-plane scaffolds land."""

__version__ = "0.0.0"
```

Create `pyproject.toml`:

```toml
[project]
name = "dcp"
version = "0.0.0"
description = "Self-hostable dbt Core control plane"
readme = "AGENTS.md"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "pytest>=8.3",
  "ruff>=0.11",
  "mypy>=1.15",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/dcp"]

[tool.ruff]
target-version = "py312"
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src", "tests"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

If hatchling packaging of `src/dcp` needs `[tool.hatch.build.targets.wheel.force-include]` or `packages = ["src/dcp"]` fails, switch to:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/dcp"]
```

or the hatch `src` layout:

```toml
[tool.hatch.build]
[tool.hatch.build.targets.wheel]
only-include = ["dcp"]

[tool.hatch.build.targets.wheel.sources]
"src/dcp" = "dcp"
```

Use whichever `uv sync` + import actually installs `dcp`. Prefer the hatch sources mapping above if the first form does not import.

Append to `.gitignore` if absent:

```
.venv/
node_modules/
dist/
*.egg-info/
.mypy_cache/
.ruff_cache/
.pytest_cache/
coverage/
```

- [ ] **Step 4: Sync and run tools**

```bash
uv sync
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run pytest
```

Expected: all pass (format may rewrite files — include those in the commit).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock src/dcp/__init__.py tests/test_smoke.py .gitignore
git commit -m "$(cat <<'EOF'
build: bootstrap uv Python package with smoke test

EOF
)"
```

---

### Task 2: pnpm workspace, www Vitest landing contract, remove Python landing unittest

**Files:**
- Create: `pnpm-workspace.yaml`
- Create: root `package.json`
- Create: `www/package.json`
- Create: `www/tsconfig.json`
- Create: `www/vitest.config.ts`
- Create: `www/tests/landing-copy.test.ts`
- Create: `package.json` scripts that filter workspace
- Delete: `tests/www/test_landing_copy.py`
- Delete: `tests/www/__init__.py` if empty and unused
- Modify: keep `www/index.html` / `www/styles.css` unchanged unless a test reveals a real contract break

**Interfaces:**
- Consumes: existing landing HTML/CSS contract from former unittest
- Produces: `pnpm --filter @dcp/www test` as verification entrypoint

- [ ] **Step 1: Write failing Vitest landing tests**

Create `www/tests/landing-copy.test.ts`:

```typescript
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const wwwRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const indexPath = join(wwwRoot, "index.html");
const stylesPath = join(wwwRoot, "styles.css");
const PRIMARY_CTA_HREF = 'href="https://github.com/juanjodevio/dcp"';

const REQUIRED = [
  "dcp",
  "dbt Core",
  "Elementary",
  "Docker Compose",
  "self-host",
  "https://github.com/juanjodevio/dcp",
] as const;

const BANNED = ["sign up", "pricing", "start free", "open app"] as const;

describe("landing copy contract", () => {
  it("has index.html", () => {
    expect(existsSync(indexPath)).toBe(true);
  });

  it("has styles.css linked from index", () => {
    expect(existsSync(stylesPath)).toBe(true);
    const html = readFileSync(indexPath, "utf8");
    expect(html).toContain("styles.css");
  });

  it("includes required copy", () => {
    const html = readFileSync(indexPath, "utf8");
    for (const needle of REQUIRED) {
      expect(html, `missing ${needle}`).toContain(needle);
    }
  });

  it("omits banned SaaS CTA phrases", () => {
    const html = readFileSync(indexPath, "utf8").toLowerCase();
    for (const banned of BANNED) {
      expect(html, `banned phrase present: ${banned}`).not.toContain(banned);
    }
  });

  it("has skip link and main landmark", () => {
    const html = readFileSync(indexPath, "utf8");
    expect(html).toContain('href="#main"');
    expect(html).toContain('id="main"');
  });

  it("uses the primary GitHub CTA href", () => {
    const html = readFileSync(indexPath, "utf8");
    expect(html).toContain(PRIMARY_CTA_HREF);
  });

  it("references existing image and font assets", () => {
    const html = readFileSync(indexPath, "utf8");
    const css = readFileSync(stylesPath, "utf8");
    const images = [...html.matchAll(/(?:src|srcset)="(img\/[^"]+)"/g)].map((m) => m[1]);
    const fonts = [...css.matchAll(/url\("([^"]+\.woff2)"\)/g)].map((m) => m[1]);
    expect(images.length).toBeGreaterThanOrEqual(1);
    expect(fonts).toHaveLength(2);
    for (const rel of [...images, ...fonts]) {
      expect(existsSync(join(wwwRoot, rel)), `missing ${rel}`).toBe(true);
    }
  });
});
```

Create `www/package.json`:

```json
{
  "name": "@dcp/www",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "lint": "eslint .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit"
  },
  "devDependencies": {
    "@types/node": "^22.13.10",
    "typescript": "^5.8.2",
    "vitest": "^3.0.9"
  }
}
```

Create `www/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noEmit": true,
    "types": ["node"]
  },
  "include": ["tests/**/*.ts", "vitest.config.ts"]
}
```

Create `www/vitest.config.ts`:

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
  },
});
```

Create `pnpm-workspace.yaml`:

```yaml
packages:
  - "www"
  - "control-plane/ui"
```

Create root `package.json` (UI package lands in Task 3; for now only `www` may exist — either create a stub `control-plane/ui/package.json` in this task or temporarily list only `www` and expand in Task 3. Prefer creating a minimal stub UI `package.json` name `@dcp/ui` with empty scripts so the workspace file is final):

```json
{
  "name": "dcp",
  "private": true,
  "packageManager": "pnpm@9.15.9",
  "scripts": {
    "lint": "pnpm -r run lint",
    "format:check": "pnpm -r run format:check",
    "typecheck": "pnpm -r run typecheck",
    "test": "pnpm -r run test"
  }
}
```

If Task 3 has not created `@dcp/ui` yet, either (a) complete Task 3 before running root `pnpm -r`, or (b) create the Task 3 UI package files in the same commit series before root recursive scripts. **Implementer: finish Task 3 package skeleton before relying on `pnpm -r`.** For this task’s verification, use:

```bash
pnpm --filter @dcp/www test
```

- [ ] **Step 2: Install and run www tests (expect PASS — landing already exists)**

```bash
corepack enable
pnpm install
pnpm --filter @dcp/www test
```

Expected: PASS (all landing contract tests green).

If FAIL on missing assets, fix only the test path regex or report a real landing bug — do not weaken the contract.

- [ ] **Step 3: Add minimal lint/format/typecheck for www**

For www-only until UI exists, make lint/format scripts no-op-safe or install eslint/prettier at root in Task 3. Minimum for this task: `typecheck` and `test` work:

```bash
pnpm --filter @dcp/www typecheck
pnpm --filter @dcp/www test
```

Expected: PASS.

- [ ] **Step 4: Remove Python landing unittest**

```bash
rm -f tests/www/test_landing_copy.py tests/www/__init__.py
rmdir tests/www 2>/dev/null || true
```

Confirm old entrypoint is gone:

```bash
python3 -m unittest tests/www/test_landing_copy.py
```

Expected: FAIL (module/path missing).

- [ ] **Step 5: Commit**

```bash
git add pnpm-workspace.yaml package.json pnpm-lock.yaml www/package.json www/tsconfig.json www/vitest.config.ts www/tests/landing-copy.test.ts
git add -u tests/www
git commit -m "$(cat <<'EOF'
test: move landing copy contract to www Vitest

EOF
)"
```

---

### Task 3: `control-plane/ui` TypeScript smoke + workspace lint/format

**Files:**
- Create: `control-plane/ui/package.json`
- Create: `control-plane/ui/tsconfig.json`
- Create: `control-plane/ui/vitest.config.ts`
- Create: `control-plane/ui/src/smoke.ts`
- Create: `control-plane/ui/src/smoke.test.ts`
- Create: `eslint.config.js` (root flat config covering `www` and `control-plane/ui`)
- Create: `.prettierrc` / `.prettierignore`
- Modify: root `package.json` / `www/package.json` to share eslint/prettier as needed
- Modify: `pnpm-lock.yaml` via `pnpm install`

**Interfaces:**
- Consumes: pnpm workspace from Task 2
- Produces: `smokeLabel(): string` returning `"dcp-ui-ok"`; Vitest covers it; root `pnpm lint|format:check|typecheck|test` green

- [ ] **Step 1: Write failing UI smoke test**

Create `control-plane/ui/src/smoke.test.ts`:

```typescript
import { describe, expect, it } from "vitest";
import { smokeLabel } from "./smoke.js";

describe("ui smoke", () => {
  it("returns the placeholder label", () => {
    expect(smokeLabel()).toBe("dcp-ui-ok");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

After creating `control-plane/ui/package.json` with vitest and installing:

```bash
pnpm --filter @dcp/ui test
```

Expected: FAIL (`smoke` module missing or `smokeLabel` not defined).

- [ ] **Step 3: Implement smoke module and package config**

Create `control-plane/ui/src/smoke.ts`:

```typescript
export function smokeLabel(): string {
  return "dcp-ui-ok";
}
```

Create `control-plane/ui/package.json`:

```json
{
  "name": "@dcp/ui",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "lint": "eslint .",
    "format:check": "prettier --check .",
    "typecheck": "tsc --noEmit"
  },
  "devDependencies": {
    "typescript": "^5.8.2",
    "vitest": "^3.0.9"
  }
}
```

Create `control-plane/ui/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noEmit": true,
    "rootDir": "src"
  },
  "include": ["src/**/*.ts"]
}
```

Create `control-plane/ui/vitest.config.ts`:

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
  },
});
```

Add root ESLint flat config `eslint.config.js`:

```javascript
import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    ignores: ["**/node_modules/**", "**/dist/**"],
  },
);
```

Add root `.prettierrc`:

```json
{
  "semi": true,
  "singleQuote": false,
  "trailingComma": "all",
  "printWidth": 100
}
```

Add `.prettierignore`:

```
pnpm-lock.yaml
uv.lock
dist
node_modules
.venv
www/img
www/fonts
```

Hoist eslint/prettier/typescript-eslint to the root `package.json` `devDependencies` and wire both packages’ `lint` / `format:check` to work from package dirs (or run eslint/prettier only from root scripts — either is fine if CI uses the same commands as `TECH.md`).

Example root `devDependencies` to add:

```json
{
  "devDependencies": {
    "@eslint/js": "^9.22.0",
    "eslint": "^9.22.0",
    "prettier": "^3.5.3",
    "typescript-eslint": "^8.26.1"
  }
}
```

Update `@dcp/www` `package.json` scripts so `lint` and `format:check` invoke eslint/prettier with configs that exist (same as UI).

- [ ] **Step 4: Install and verify full TS workspace**

```bash
pnpm install
pnpm lint
pnpm format:check
pnpm typecheck
pnpm test
```

Expected: all PASS. If Prettier wants rewrites, run `pnpm exec prettier --write .` then re-check.

- [ ] **Step 5: Commit**

```bash
git add control-plane/ui package.json pnpm-lock.yaml eslint.config.js .prettierrc .prettierignore www/package.json
git commit -m "$(cat <<'EOF'
build: add ui TypeScript smoke and workspace lint

EOF
)"
```

---

### Task 4: GitHub Actions CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: Task 1–3 lockfiles and scripts
- Produces: Actions jobs with `name: python` and `name: typescript` (these strings are the required-check contract)

- [ ] **Step 1: Write the workflow**

Create `.github/workflows/ci.yml`:

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [dev, main]

permissions:
  contents: read

env:
  TZ: UTC

jobs:
  python:
    name: python
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - name: Sync
        run: uv sync --frozen
      - name: Ruff check
        run: uv run ruff check .
      - name: Ruff format
        run: uv run ruff format --check .
      - name: Mypy
        run: uv run mypy .
      - name: Pytest
        run: uv run pytest

  typescript:
    name: typescript
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: pnpm
      - name: Install
        run: pnpm install --frozen-lockfile
      - name: Lint
        run: pnpm lint
      - name: Format
        run: pnpm format:check
      - name: Typecheck
        run: pnpm typecheck
      - name: Test
        run: pnpm test
```

Do not add path filters. Do not add AI-review jobs.

- [ ] **Step 2: Sanity-check YAML locally**

```bash
python3 -c "import pathlib; print(pathlib.Path('.github/workflows/ci.yml').read_text()[:40])"
```

Expected: prints workflow header text. (Full Actions run happens after push.)

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "$(cat <<'EOF'
ci: add python and typescript required check jobs

EOF
)"
```

---

### Task 5: ADR-0008, steering docs, agent-delivery notes

**Files:**
- Create: `docs/adr/0008-node-package-manager-pnpm.md`
- Modify: `docs/adr/index.md`
- Modify: `docs/adr/0007-python-package-manager-uv.md` (Node line: now decided via ADR-0008)
- Modify: `docs/TECH.md`
- Modify: `docs/STRUCTURE.md`
- Modify: `AGENTS.md`
- Modify: `.cursor/skills/agent-delivery/SKILL.md` (finish: human arms auto-merge; verification command)
- Modify: `docs/superpowers/specs/2026-08-31-repo-ci-automerge-setup-design.md` Status → Accepted (optional but preferred)

**Interfaces:**
- Consumes: exact commands from Tasks 1–4
- Produces: durable verification entrypoint `pnpm --filter @dcp/www test`

- [ ] **Step 1: Write ADR-0008**

Create `docs/adr/0008-node-package-manager-pnpm.md`:

```markdown
# Node package manager: pnpm

Status: Accepted
Date: 2026-08-31

## Context And Problem Statement

TypeScript packages (`www` test tooling and planned `control-plane/ui`) need a single Node package manager so agents and CI do not diverge across npm, yarn, and pnpm.

## Decision Drivers

- Lockfile-based reproducible installs
- Workspace support for multiple packages in one repo
- Common default for modern Next.js / TS monorepos

## Considered Options

- pnpm
- npm
- yarn

## Decision Outcome

Chosen option: "pnpm", because it is locked as the Node package manager for this repository. Expect root `pnpm-workspace.yaml` and `pnpm-lock.yaml`. Installs in CI use `pnpm install --frozen-lockfile`.

## Consequences

- Good, because UI and landing test tooling share one workspace convention
- Bad, because contributors need Corepack/pnpm available
- Neutral: marketing landing HTML/CSS remains static; Node under `www/` is for tests/CI only

## Confirmation

`docs/TECH.md` and CI reference pnpm; no npm/yarn lockfiles are introduced as source of truth.

## More Information

- `docs/TECH.md`
- `docs/superpowers/specs/2026-08-31-repo-ci-automerge-setup-design.md`
```

Add a row to `docs/adr/index.md` for ADR-0008.

In ADR-0007 Consequences, change the Node line from undecided to “see ADR-0008 (pnpm)”.

- [ ] **Step 2: Update TECH.md Commands / Package Manager**

Set Python and Node package managers as locked. Replace the unittest verification entrypoint with:

```bash
pnpm --filter @dcp/www test
```

Document full local CI parity:

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
pnpm install --frozen-lockfile
pnpm lint
pnpm format:check
pnpm typecheck
pnpm test
```

Mark landing Vitest as verified after first successful local run; note Actions job names `python` and `typescript`.

State AI PR review is deferred (CodeRabbit radar); no review secrets in CI.

- [ ] **Step 3: Update STRUCTURE.md**

Document present `.github/workflows/`, `src/dcp/`, pnpm workspace (`www`, `control-plane/ui`), and that landing tests live in `www/tests/`. Note `tests/www` Python landing tests are removed.

- [ ] **Step 4: Update AGENTS.md Commands**

Verification entrypoint must be exactly the TECH-owned command:

```bash
pnpm --filter @dcp/www test
```

Mention uv + pnpm ADRs. Do not duplicate full CI matrix in AGENTS.md.

- [ ] **Step 5: Update agent-delivery finish notes**

In `.cursor/skills/agent-delivery/SKILL.md`, ensure finish toward `dev` still **never merges** and **never enables auto-merge**. Add one explicit sentence: humans arm auto-merge on the PR after the agent opens a ready-for-review PR. Verification evidence uses the AGENTS.md entrypoint.

- [ ] **Step 6: Commit**

```bash
git add docs/adr/0008-node-package-manager-pnpm.md docs/adr/index.md docs/adr/0007-python-package-manager-uv.md docs/TECH.md docs/STRUCTURE.md AGENTS.md .cursor/skills/agent-delivery/SKILL.md
git commit -m "$(cat <<'EOF'
docs: lock pnpm and CI verification entrypoint

EOF
)"
```

---

### Task 6: GitHub repo auto-merge and rulesets (`gh`)

**Files:**
- None required in git (ops). Optionally create: `docs/superpowers/specs/` note already covers behavior — if a short runbook snippet is needed, add under `docs/TECH.md` a “Repository gates” subsection with the commands below (preferred so agents can re-read them).

**Interfaces:**
- Consumes: CI job names `python`, `typescript` must have appeared on the repo at least once
- Produces: `allow_auto_merge=true`; rulesets protecting `dev` and `main`

**Ordering:** Land/push Tasks 1–5 so Actions runs once (PR or push to `dev`) **before** attaching required checks to rulesets. GitHub only lists check contexts after they have run.

- [ ] **Step 1: Enable repository auto-merge**

```bash
gh repo edit --enable-auto-merge
```

Expected: command succeeds. Confirm:

```bash
gh api repos/:owner/:repo --jq .allow_auto_merge
```

Expected: `true`

- [ ] **Step 2: Ensure CI check contexts exist**

Open a PR into `dev` (or push this branch and use an existing PR) and wait until jobs `python` and `typescript` complete once.

```bash
gh pr checks
```

Expected: both names visible (pass or fail — existence matters for ruleset selection; they should pass).

- [ ] **Step 3: Create ruleset for `dev`**

Use GitHub rulesets API (adjust owner/repo via `gh`):

```bash
gh api repos/:owner/:repo/rulesets --method POST --input - <<'EOF'
{
  "name": "protect-dev",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/heads/dev"],
      "exclude": []
    }
  },
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          {"context": "python"},
          {"context": "typescript"}
        ]
      }
    }
  ]
}
EOF
```

If the API rejects `deletion` / `non_fast_forward` shapes for your plan tier, create the equivalent ruleset in the GitHub UI with: block deletions, block force pushes, require PR, required checks `python` + `typescript`, required approvals = 0. Record the working payload in `docs/TECH.md`.

- [ ] **Step 4: Create ruleset for `main`**

Same as `dev` but `include: ["refs/heads/main"]` and name `protect-main`. Do **not** rely on auto-merge for `main` (humans merge release PRs). Required checks still `python` + `typescript`.

- [ ] **Step 5: Document human arming in TECH.md**

Add a short subsection:

```markdown
## Repository gates

- Feature PRs target `dev`. After CI is green, a human enables auto-merge (squash): `gh pr merge --auto --squash` or the PR UI.
- `/agent-delivery` must not enable auto-merge.
- Milestone releases: human merges `dev` → `main`.
- AI PR review (CodeRabbit) is deferred.
```

Commit if TECH was not already updated in Task 5:

```bash
git add docs/TECH.md
git commit -m "$(cat <<'EOF'
docs: document human auto-merge arming and rulesets

EOF
)"
```

- [ ] **Step 6: Verify end-to-end manually**

1. Open a no-op PR into `dev`.
2. Confirm checks `python` and `typescript` run.
3. As human: `gh pr merge --auto --squash`.
4. Confirm merge occurs when green without an approving review.
5. Confirm direct push to `dev` is rejected.

Expected: matches design success criteria 1–3 and 7.

---

## Plan self-review

| Spec item | Task |
|-----------|------|
| uv + Ruff/mypy/pytest | Task 1 |
| pnpm + ESLint/Prettier/tsc/Vitest | Tasks 2–3 |
| Landing → Vitest under `www/`; delete Python unittest | Task 2 |
| CI jobs `python` + `typescript`, always-run | Task 4 |
| ADR pnpm + TECH/STRUCTURE/AGENTS | Task 5 |
| Human arms auto-merge; agent does not | Tasks 5–6 |
| Rulesets + `allow_auto_merge` | Task 6 |
| Deferred CodeRabbit/Codex | Tasks 4–5 (explicit absence + TECH note) |
| Cursor Cloud targets `dev`, ready-for-review PR | Task 5 agent-delivery note |

No TBD placeholders left. Hatch `src/dcp` packaging has an explicit fallback if the first wheel layout fails.
