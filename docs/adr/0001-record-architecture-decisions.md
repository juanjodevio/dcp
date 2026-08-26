# Record architecture decisions

Status: Accepted
Date: 2026-08-25

## Context And Problem Statement

The project needs a durable place to record implementation-shaping decisions so humans and agents do not rediscover or contradict them in chat.

## Decision Drivers

- Agent-readable durable truth
- Lightweight process for an early open-source repo
- Compatibility with common ADR naming

## Considered Options

- Markdown ADRs under `docs/adr/`
- Decisions only in chat / session handoff
- Full Architecture Decision Records tooling mandatory from day one

## Decision Outcome

Chosen option: "Markdown ADRs under `docs/adr/`", because it matches product-steering conventions and works without `adr-tools`.

## Consequences

- Good, because decisions are reviewable in git
- Bad, because numbering/index must be maintained manually until tooling is adopted

## Confirmation

New durable decisions appear as numbered files and a row in `docs/adr/index.md`.

## More Information

- `docs/ROADMAP.md`, `docs/TECH.md`
