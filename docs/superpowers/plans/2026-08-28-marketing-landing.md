# Marketing Landing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a static public landing at `www/` that explains dcp and links to GitHub before any control-plane application code exists.

**Architecture:** One HTML page and one stylesheet at repo root `www/`. No Next.js, no npm, no Compose. Copy is locked by unittest against `www/index.html`. Visual treatment uses the landing skill pack (`design-taste-frontend` + `web-design-guidelines`), not `.cursor/agents/frontend-developer.md`.

**Tech Stack:** HTML5, CSS, Python 3 stdlib `unittest` and `http.server`.

## Global Constraints

- Files only under `www/` (`index.html`, `styles.css`) plus `tests/www/test_landing_copy.py`.
- No Next.js, no `package.json`, no files under `control-plane/ui/`.
- Visible copy must include: `dcp`, `dbt Core`, `Elementary`, `Docker Compose`, `self-host`, `https://github.com/juanjodevio/dcp`.
- Banned visible phrases (case-insensitive): `sign up`, `pricing`, `start free`, `open app`.
- Primary CTA href is exactly `https://github.com/juanjodevio/dcp`.
- Invoke `design-taste-frontend` for visual polish; do not invent product features.
- Do not edit steering docs or ADRs in this plan.

---

### Task 1: Landing copy contract tests

**Files:**
- Create: `tests/www/test_landing_copy.py`
- Create: `tests/www/__init__.py` (empty)

**Interfaces:**
- Consumes: nothing
- Produces: unittest module `tests.www.test_landing_copy` that fails until `www/index.html` and `www/styles.css` exist with required copy

- [ ] **Step 1: Write the failing tests**

Create `tests/www/__init__.py` as an empty file.

Create `tests/www/test_landing_copy.py`:

```python
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INDEX = ROOT / "www" / "index.html"
STYLES = ROOT / "www" / "styles.css"

REQUIRED = (
    "dcp",
    "dbt Core",
    "Elementary",
    "Docker Compose",
    "self-host",
    "https://github.com/juanjodevio/dcp",
)

BANNED = (
    "sign up",
    "pricing",
    "start free",
    "open app",
)


class LandingCopyTests(unittest.TestCase):
    def test_index_exists(self):
        self.assertTrue(INDEX.is_file(), f"missing {INDEX}")

    def test_styles_exist_and_are_linked(self):
        self.assertTrue(STYLES.is_file(), f"missing {STYLES}")
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn("styles.css", html)

    def test_required_copy(self):
        html = INDEX.read_text(encoding="utf-8")
        for needle in REQUIRED:
            with self.subTest(needle=needle):
                self.assertIn(needle, html)

    def test_no_saas_cta(self):
        html = INDEX.read_text(encoding="utf-8").lower()
        for banned in BANNED:
            with self.subTest(banned=banned):
                self.assertNotIn(banned, html)

    def test_skip_link_and_main(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="#main"', html)
        self.assertIn('id="main"', html)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
python3 -m unittest tests/www/test_landing_copy.py
```

Expected: FAIL with `missing .../www/index.html` (or styles missing). Do not proceed if tests pass.

- [ ] **Step 3: Commit**

```bash
git add tests/www/__init__.py tests/www/test_landing_copy.py
git commit -m "$(cat <<'EOF'
test: add marketing landing copy contract

EOF
)"
```

---

### Task 2: Semantic landing HTML

**Files:**
- Create: `www/index.html`
- Create: `www/styles.css` (minimal stub so the stylesheet test can pass; Task 3 replaces it)

**Interfaces:**
- Consumes: required/banned strings from Task 1
- Produces: `www/index.html` with skip link, `#main`, GitHub CTA, and all required copy

- [ ] **Step 1: Write index.html and a stub stylesheet**

Create `www/styles.css`:

```css
/* Replaced in Task 3. */
body {
  font-family: ui-sans-serif, system-ui, sans-serif;
}
```

Create `www/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>dcp — self-hostable dbt Core control plane</title>
    <meta
      name="description"
      content="Open-source, self-hostable control plane for dbt Core with Elementary. Run jobs on Docker Compose."
    />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>
    <header>
      <p class="mark">dcp</p>
      <a class="cta" href="https://github.com/juanjodevio/dcp">View on GitHub</a>
    </header>
    <main id="main">
      <section class="hero">
        <h1>Open-source control plane for dbt Core</h1>
        <p>
          dcp is a self-hostable alternative to commercial dbt Cloud–like ops:
          projects, jobs, runs, artifacts, lineage, and Elementary — without
          locking the core to one cloud or orchestrator.
        </p>
        <p>
          The product is under active development in this repository. This page
          is the public face until Docker Compose ships.
        </p>
        <a class="cta" href="https://github.com/juanjodevio/dcp">View on GitHub</a>
      </section>
      <section>
        <h2>Why it exists</h2>
        <p>
          Teams that want Cloud-like job and run UX around dbt Core either buy a
          vendor stack or glue CI, schedulers, and scripts. dcp centralizes that
          operator workflow and keeps dbt’s model DAG inside dbt.
        </p>
      </section>
      <section>
        <h2>What v0.1 covers</h2>
        <ul>
          <li>Projects, environments, jobs, and schedules</li>
          <li>Manual and cron-driven runs with logs and artifacts</li>
          <li>Basic lineage from dbt artifacts</li>
          <li>Elementary as required observability</li>
          <li>Local Docker runner, optional AWS Batch, packaged with Docker Compose</li>
        </ul>
      </section>
      <section>
        <h2>How you run it</h2>
        <p>
          You self-host. v0.1 is single-user with no auth — bind it privately.
          Compose, including a required local dbt runner image, is the packaging
          target. Nothing here is a hosted SaaS.
        </p>
      </section>
    </main>
    <footer>
      <p>
        <a href="https://github.com/juanjodevio/dcp">github.com/juanjodevio/dcp</a>
      </p>
    </footer>
  </body>
</html>
```

- [ ] **Step 2: Run tests to verify they pass**

Run:

```bash
python3 -m unittest tests/www/test_landing_copy.py
```

Expected: `OK` (5 tests). If `self-host` fails, the word must appear as that exact substring (already in “self-hostable” and “self-host” above).

- [ ] **Step 3: Commit**

```bash
git add www/index.html www/styles.css
git commit -m "$(cat <<'EOF'
feat: add static marketing landing markup

EOF
)"
```

---

### Task 3: Landing visual language

**Files:**
- Modify: `www/styles.css`
- Modify: `www/index.html` only if class names are required for layout; do not drop required copy

**Interfaces:**
- Consumes: `www/index.html` from Task 2
- Produces: a complete `www/styles.css` suitable for a technical OSS landing (not a dashboard, not a SaaS waitlist)

- [ ] **Step 1: Load the landing skill pack**

Read and follow `design-taste-frontend` (taste-skill v2) and `web-design-guidelines`. Infer this as: B2B OSS landing for data engineers, Linear/HashiCorp-adjacent, low motion, high information density relative to a consumer landing. Do not use Inter-on-purple, centered three-card feature grids, or glassmorphism as the default.

- [ ] **Step 2: Replace the stub stylesheet**

Overwrite `www/styles.css` with a full sheet. Minimum bar if taste-skill is unavailable: the following file (implementers should still apply the skill and may replace values, not structure):

```css
:root {
  color-scheme: dark;
  --bg: #0b0c0e;
  --fg: #ececec;
  --muted: #9a9aa3;
  --line: #2a2b31;
  --accent: #c8f542;
  --max: 44rem;
}

* {
  box-sizing: border-box;
}

html {
  background: var(--bg);
  color: var(--fg);
}

body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, sans-serif;
  line-height: 1.5;
}

.skip-link {
  position: absolute;
  left: 0.75rem;
  top: -3rem;
  background: var(--fg);
  color: var(--bg);
  padding: 0.35rem 0.6rem;
}

.skip-link:focus {
  top: 0.75rem;
}

header,
footer,
main {
  max-width: calc(var(--max) + 8rem);
  margin: 0 auto;
  padding: 1.25rem 1.5rem;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--line);
}

.mark {
  margin: 0;
  font-family: ui-monospace, monospace;
  letter-spacing: 0.08em;
  text-transform: lowercase;
}

.cta {
  display: inline-block;
  color: var(--bg);
  background: var(--accent);
  text-decoration: none;
  padding: 0.45rem 0.8rem;
  font-weight: 600;
}

.cta:focus-visible,
a:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

.hero h1 {
  font-size: clamp(2rem, 5vw, 3.25rem);
  line-height: 1.1;
  letter-spacing: -0.03em;
  max-width: 18ch;
}

section + section {
  border-top: 1px solid var(--line);
  margin-top: 2.5rem;
  padding-top: 2.5rem;
}

h2 {
  font-size: 1rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

ul {
  padding-left: 1.1rem;
}

footer {
  border-top: 1px solid var(--line);
  color: var(--muted);
}

footer a {
  color: var(--fg);
}
```

- [ ] **Step 3: Re-run copy tests**

Run:

```bash
python3 -m unittest tests/www/test_landing_copy.py
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add www/styles.css www/index.html
git commit -m "$(cat <<'EOF'
style: apply marketing landing visual language

EOF
)"
```

---

### Task 4: Local preview verification

**Files:**
- None required (preview only)

**Interfaces:**
- Consumes: `www/` from Tasks 2–3
- Produces: human confirmation the page is a landing, not Getting started or a dashboard

- [ ] **Step 1: Serve the directory**

Run:

```bash
python3 -m http.server -d www 4173
```

Expected: server listening; `http://127.0.0.1:4173/` returns the landing.

- [ ] **Step 2: Browser check**

Open `http://127.0.0.1:4173/`. Confirm: skip link works on Tab, primary CTA goes to GitHub, no signup/pricing, page does not resemble an app shell. Optionally use `agent-browser` (`agent-browser open http://127.0.0.1:4173/` then snapshot). Stop the server when done (`Ctrl+C`).

- [ ] **Step 3: Commit only if Step 2 forced markup fixes**

If HTML/CSS changed:

```bash
git add www/
git commit -m "$(cat <<'EOF'
fix: address landing preview accessibility and CTA

EOF
)"
```

If nothing changed, skip the commit.
