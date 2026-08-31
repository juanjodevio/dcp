# Python package manager: uv

Status: Accepted
Date: 2026-08-25

## Context And Problem Statement

The Python control-plane packages need a single canonical package manager before scaffolds and lockfiles land, so agents and CI do not diverge across pip, poetry, and uv.

## Decision Drivers

- Fast, reproducible installs with a lockfile
- First-class `pyproject.toml` workflow
- Consistent agent/CI commands

## Considered Options

- uv
- Poetry
- pip + requirements.txt / pip-tools

## Decision Outcome

Chosen option: "uv", because it is locked as the Python package manager for this repository. Expect `pyproject.toml` and `uv.lock`. Dependency sync and tool invocation should go through `uv` / `uv run`.

## Consequences

- Good, because install and lockfile conventions are unambiguous for agents
- Bad, because contributors must have uv available (document in adopter/dev docs)
- Neutral: Node/UI package manager remains undecided

## Confirmation

Python manifests use uv; CI and `docs/TECH.md` commands reference `uv`; no Poetry lockfiles are introduced.

## More Information

- `docs/TECH.md`
