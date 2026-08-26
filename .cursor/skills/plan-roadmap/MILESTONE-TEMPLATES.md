# Roadmap Planning Templates

Use every heading. Write `None` when a non-verdict section has no entries.

## Roadmap authoring forms

This section is the single canonical contract shared by roadmap authors and every validator. No other section restates these forms. Parse with the exact patterns below so no approved identifier is silently omitted and no mere mention of an identifier is mistaken for a declaration.

Milestone heading, one per milestone:

`## M<number> <separator> milestone name`

`<separator>` is an em dash `—`, an en dash `–`, or a hyphen-minus `-`, with at least one space or tab on each side. All three separators are equally valid and none may be dropped from parsing.

Deliverable bullet, inside a milestone section:

`- [M<number>-D<number>] deliverable outcome`

The bullet marker may be `-`, `*`, or `+`. Any amount of leading space or tab indentation is allowed, and an indented deliverable is still a deliverable.

Milestone Linear ticket references, at most one line per milestone section:

`Linear tickets: TEAM-123, TEAM-124`

A milestone never carries more than one `Linear tickets:` line. New identifiers are appended to the existing line in place, and a stale identifier is replaced on that same line. A second reference line is never added.

Target Linear team key, exactly one line under `## Delivery Workflow` in root `AGENTS.md`:

`Linear team: <team-key>`

`Linear tickets:` and `Linear team:` both accept an optional Markdown bullet prefix, so `Linear team: ENG` and `- Linear team: ENG` are equally valid.

Every synced Linear issue description carries `Roadmap sync key: M<number>` for a milestone parent or `Roadmap sync key: M<number>-D<number>` for a deliverable, governed by the sync-key exactness rules below.

### Required parsing patterns

Apply these patterns per line, anchored, with no substring shortcuts:

- Milestone heading: `^[ \t]*##[ \t]+(M\d+)[ \t]+[—–-][ \t]+(\S.*)$`
- Deliverable bullet: `^[ \t]*[-*+][ \t]+\[(M\d+-D\d+)\][ \t]+(\S.*)$`
- Milestone ticket references: `^[ \t]*(?:[-*+][ \t]+)?Linear tickets:[ \t]*(\S.*?)[ \t]*$`
- Linear team key: `^[ \t]*(?:[-*+][ \t]+)?Linear team:[ \t]*([^\s<>]+)[ \t]*$`
- Linear issue sync key: `^[ \t]*Roadmap sync key:[ \t]*(\S.*?)[ \t]*$`
- Linear issue dependency references: `^[ \t]*Depends on:[ \t]*(\S.*?)[ \t]*$`
- Linear issue parent reference: `^[ \t]*Parent sync key:[ \t]*(\S.*?)[ \t]*$`

### Malformed declaration detectors

Only a line that claims to be a declaration may block. A heading or sentence that merely mentions an identifier is never a declaration and never blocks. Apply these detectors per line:

- Milestone declaration candidate: `^[ \t]*##(?!#)[ \t]+M\d+(?![\w-])`
- Deliverable declaration candidate: `^[ \t]*[-*+][ \t]+\[M\d+-D\d+\](?!\()`

The milestone detector requires exactly two `#` characters and requires `M<number>` to be the first content token, so `### Deliverables for M1` and `## Deliverables for M1` are never candidates.

The deliverable detector requires a list bullet whose first token is `[M<number>-D<number>]`, and it excludes the Markdown link form, so `See [M1-D2] for the migration detail.` and `- [M1-D2](https://example.com/m1-d2)` are never candidates.

A candidate line that fails its allowed pattern above is BLOCKED for human correction and is never silently skipped. `## M4` blocks because it omits the separator and the milestone name. `- [M1-D9]` blocks because it omits the outcome text. A line that is not a candidate is neither parsed as an identifier nor blocked.

Duplicate approved milestone identifiers and duplicate approved deliverable identifiers are BLOCKED on every run, including a run scoped to a single milestone.

## Sync-key exactness

`Roadmap sync key:` occupies its own line, appears exactly once per Linear issue description, and carries one key matching `^M\d+$` or `^M\d+-D\d+$`.

Sync keys are immutable. A renamed outcome keeps its existing key.

Parse the key as the trimmed remainder of that line, then compare keys only by full-value equality of parsed keys. Never compare by substring, prefix, suffix, or containment. `M1` never matches `M10`, `M1-D1` never matches `M1-D10`, and `M1` never matches `M1-D1`.

Linear description search is a substring or full-text operation, so it returns prefix neighbours. Re-parse every search result and keep only exact parsed-key equality matches before duplicate detection, before classification, and inside every pre-create recheck.

An issue whose description carries zero or more than one `Roadmap sync key:` line is BLOCKED for human reconciliation and receives no mutation.

Dependency and parent references never reuse the sync-key field. Dependencies use `Depends on:` and a parent uses `Parent sync key:`. A value parsed from `Depends on:` or `Parent sync key:` is never counted as that issue's own sync key.

## Milestone activity derivation

A milestone's activity comes from the Linear ticket references recorded in its approved roadmap section, never from roadmap prose or ordering:

- ACTIVE when the milestone carries no `Linear tickets:` line, or that line lists no identifier.
- ACTIVE when at least one referenced ticket resolves to a nonterminal state.
- COMPLETE when every referenced ticket resolves and every one is in a completed state. Report it and generate no fresh drafts for it.
- NEEDS_HUMAN_RECONCILIATION when any referenced ticket is canceled, fails to resolve, or resolves to a sync key that contradicts the milestone. Generate no fresh drafts for it and state the exact human action.

Never delete or rewrite an existing reference, and never treat COMPLETE as authorization to create work.

## Roadmap Coverage Report

### Approved roadmap SHA
### Roadmap authority mode
Use `local-main-bootstrap` or `origin-main`.
### Linear team key
### Linear team key source
Record the exact approved `AGENTS.md` line the team key was parsed from.
### Milestones inspected
### Milestone activity
Record ACTIVE, COMPLETE, or NEEDS_HUMAN_RECONCILIATION per milestone with its referenced ticket identifiers.
### Covered deliverables
### Missing deliverables
### Duplicate roadmap keys
### Duplicate sync keys
### Active-ticket conflicts
### Stale draft tickets
### Ambiguities
### Result
Use `READY_TO_SYNC` or `BLOCKED`.

## Milestone Plan

### Milestone ID and outcome
### Completion evidence
### Deliverables
For each deliverable include sync key, title, outcome, acceptance criteria, verification, dependencies, contracts, risks, and suggested Linear state.
### Integration work
### Release work
### Milestone risks
### Result
Use `READY_TO_SYNC` or `BLOCKED`.

## Linear Milestone Parent

### Title
Use `Milestone M<number>: milestone name`.
### Description
Include roadmap outcome, completion evidence, risks, and exactly one `Roadmap sync key: M<number>` line.
### State
Use `Draft` or `Needs Planning`.

## Linear Deliverable Ticket

### Title
### Description
Include outcome, acceptance criteria, verification, contracts, risks, a `Depends on:` line for dependency references, and exactly one `Roadmap sync key: M<number>-D<number>` line.
### Parent sync key
### Dependency sync keys
### State
Use `Draft` or `Needs Planning`.

## Reconciliation Report

### Approved roadmap SHA
### Roadmap authority mode
### Run identifier
### Linear team key
### Linear team key source
### Linear pagination proof
### Exact-key filter proof
### Relation mutation schema proof
### Milestone activity
### Created tickets
### Refined tickets
### Unchanged tickets
### Skipped active tickets
### Duplicate roadmap keys
### Duplicate conflicts
### Unsupported mutations
### Stale draft tickets
### Roadmap link pull request
### Remaining coverage gaps
### Result
Use `SYNCED`, `PARTIAL`, or `BLOCKED`.
