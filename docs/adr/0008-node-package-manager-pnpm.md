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
