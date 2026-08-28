# Roadmap Planning Templates

Use every heading. Write `None` when a non-verdict section has no entries.

## Roadmap authoring forms

This section is the single canonical contract shared by roadmap authors and every validator. No other section restates these forms. Parse with the exact patterns below so no approved identifier is silently omitted and no mere mention of an identifier is mistaken for a declaration.

Milestone heading, one per milestone:

`## M<number> <separator> milestone name`

`<separator>` is an em dash `—`, an en dash `–`, or a hyphen-minus `-`, with at least one space or tab on each side. All three separators are equally valid and none may be dropped from parsing.

Each roadmap milestone maps to exactly one Linear **project** (not a parent issue). Deliverables map to Linear **issues** inside that project.

Deliverable bullet, inside a milestone section.

After the first `/plan-roadmap` sync, each deliverable uses a Markdown link to its Linear issue:

`- [TEAM-123](https://linear.app/<workspace>/issue/TEAM-123) deliverable outcome`

Before the first sync, or on a milestone not yet linked, deliverables may still use the bootstrap sync-key form:

`- [M<number>-D<number>] deliverable outcome`

The bullet marker may be `-`, `*`, or `+`. Any amount of leading space or tab indentation is allowed, and an indented deliverable is still a deliverable.

Milestone Linear project reference, at most one line per milestone section, immediately after the milestone heading and before deliverable bullets:

`Linear project: [M1 — Steering and design lock](https://linear.app/<workspace>/project/<slug>)`

Legacy parent-issue references remain parseable for older roadmaps but must not be added on new writes:

`Linear ticket: [TEAM-123](https://linear.app/<workspace>/issue/TEAM-123)`

`Linear tickets: TEAM-123, TEAM-124`

A milestone never carries more than one project/parent reference line (`Linear project:`, legacy `Linear ticket:`, or legacy `Linear tickets:`). A second reference line is never added.

Target Linear team key, exactly one line under `## Delivery Workflow` in root `AGENTS.md`:

`Linear team: <team-key>`

`Linear project:`, `Linear ticket:`, `Linear tickets:`, and `Linear team:` all accept an optional Markdown bullet prefix, so `- Linear team: ENG` is equally valid.

Every synced Linear **issue** description carries exactly one `Roadmap sync key: M<number>-D<number>` line for a deliverable. Every synced Linear **project** description carries exactly one `Roadmap sync key: M<number>` line for the milestone. Linked roadmap bullets identify deliverables by Linear issue identifier; the workflow resolves each identifier to its immutable sync key in Linear before planning or classification.

### Required parsing patterns

Apply these patterns per line, anchored, with no substring shortcuts:

- Milestone heading: `^[ \t]*##[ \t]+(M\d+)[ \t]+[—–-][ \t]+(\S.*)$`
- Deliverable bullet (linked): `^[ \t]*[-*+][ \t]+\[([A-Z]+-\d+)\]\([^)]+\)[ \t]+(\S.*)$`
- Deliverable bullet (bootstrap sync key): `^[ \t]*[-*+][ \t]+\[(M\d+-D\d+)\][ \t]+(\S.*)$`
- Milestone project reference (linked): `^[ \t]*(?:[-*+][ \t]+)?Linear project:[ \t]*\[([^\]]+)\]\(([^)]+)\)[ \t]*$`
- Milestone parent reference (legacy issue): `^[ \t]*(?:[-*+][ \t]+)?Linear ticket:[ \t]*\[([A-Z]+-\d+)\]\([^)]+\)[ \t]*$`
- Milestone ticket references (legacy aggregate): `^[ \t]*(?:[-*+][ \t]+)?Linear tickets:[ \t]*(\S.*?)[ \t]*$`
- Linear team key: `^[ \t]*(?:[-*+][ \t]+)?Linear team:[ \t]*([^\s<>]+)[ \t]*$`
- Linear issue or project sync key: `^[ \t]*Roadmap sync key:[ \t]*(\S.*?)[ \t]*$`
- Linear issue dependency references: `^[ \t]*Depends on:[ \t]*(\S.*?)[ \t]*$`
- Linear issue project sync key (on deliverable issues): `^[ \t]*Project sync key:[ \t]*(\S.*?)[ \t]*$`

### Deliverable identity resolution

Parse deliverable bullets with the linked pattern first, then the bootstrap sync-key pattern.

- Bootstrap bullet: deliverable sync key is the parsed `M<number>-D<number>` token.
- Linked bullet: deliverable sync key is the `Roadmap sync key:` on the Linear issue whose identifier matches the parsed `TEAM-<number>` token. When the identifier does not resolve, the sync key is missing, or the resolved sync key is not a deliverable key (`M<number>-D<number>`), return BLOCKED before Planner launch and before any Linear mutation.

Duplicate deliverable sync keys anywhere in the approved roadmap return BLOCKED on every run, including a run scoped to a single milestone. Duplicate Linear issue identifiers on linked deliverable bullets in the same milestone section also return BLOCKED.

### Milestone project identity resolution

- Canonical form: resolve the `Linear project:` URL or display name to a Linear project whose description carries `Roadmap sync key: M<number>` matching the milestone heading.
- Legacy `Linear ticket:` / `Linear tickets:` forms remain readable for migration; new writes never create milestone parent issues. When a legacy parent issue still carries `Roadmap sync key: M<number>`, report it under remaining coverage gaps and recommend canceling it after the project exists and deliverables are assigned to the project.
- BLOCKED when more than one Linear project claims the same milestone sync key, or when the linked project resolves to a different sync key than the milestone heading.

### Malformed declaration detectors

Only a line that claims to be a declaration may block. A heading or sentence that merely mentions an identifier is never a declaration and never blocks. Apply these detectors per line:

- Milestone declaration candidate: `^[ \t]*##(?!#)[ \t]+M\d+(?![\w-])`
- Linked deliverable declaration candidate: `^[ \t]*[-*+][ \t]+\[[A-Z]+-\d+\]\(`
- Bootstrap deliverable declaration candidate: `^[ \t]*[-*+][ \t]+\[M\d+-D\d+\](?!\()`

The milestone detector requires exactly two `#` characters and requires `M<number>` to be the first content token, so `### Deliverables for M1` and `## Deliverables for M1` are never candidates.

The linked deliverable detector requires a list bullet whose first token is `[TEAM-<number>](`, so `- [DCP-10](https://linear.app/...)` is a candidate.

The bootstrap deliverable detector requires a list bullet whose first token is `[M<number>-D<number>]` not followed by `(`, so `- [M1-D2] outcome` is a candidate and `- [M1-D2](https://example.com/m1-d2)` is never a bootstrap candidate.

A candidate line that fails its allowed pattern above is BLOCKED for human correction and is never silently skipped. `## M4` blocks because it omits the separator and the milestone name. `- [M1-D9]` blocks because it omits the outcome text. `- [DCP-10]` blocks because it omits the URL and outcome. A line that is not a candidate is neither parsed as an identifier nor blocked.

Duplicate approved milestone identifiers and duplicate approved deliverable sync keys are BLOCKED on every run, including a run scoped to a single milestone.

## Sync-key exactness

`Roadmap sync key:` occupies its own line, appears exactly once per Linear issue or project description, and carries one key matching `^M\d+$` (projects only) or `^M\d+-D\d+$` (deliverable issues only).

Sync keys are immutable. A renamed outcome keeps its existing key.

Parse the key as the trimmed remainder of that line, then compare keys only by full-value equality of parsed keys. Never compare by substring, prefix, suffix, or containment. `M1` never matches `M10`, `M1-D1` never matches `M1-D10`, and `M1` never matches `M1-D1`.

Linear description search is a substring or full-text operation, so it returns prefix neighbours. Re-parse every search result and keep only exact parsed-key equality matches before duplicate detection, before classification, and inside every pre-create recheck.

An issue or project whose description carries zero or more than one `Roadmap sync key:` line is BLOCKED for human reconciliation and receives no mutation.

Dependency references never reuse the sync-key field. Dependencies use `Depends on:`. A deliverable's owning milestone is the Linear **project** assignment (and optional `Project sync key: M<number>` line), never a parent issue. A value parsed from `Depends on:` or `Project sync key:` is never counted as that issue's own sync key.

## Milestone activity derivation

A milestone's activity comes from the Linear **project** and every deliverable issue in that project (plus linked deliverable bullets in the roadmap), never from roadmap prose or ordering:

Collect references from:
- the milestone `Linear project:` line, when present;
- every linked deliverable bullet `[TEAM-<number>](...)`;
- legacy `Linear ticket:` / `Linear tickets:` lines only during migration reporting.

Resolve deliverable identifiers to Linear issue state. When a linked deliverable identifier fails to resolve, derive NEEDS_HUMAN_RECONCILIATION for that milestone.

- ACTIVE when the milestone carries no resolvable deliverable references, or at least one deliverable issue resolves to a nonterminal state.
- COMPLETE when every deliverable issue resolves and every one is in a completed state (and the Linear project exists). Report it and generate no fresh drafts for it.
- NEEDS_HUMAN_RECONCILIATION when any deliverable is canceled, fails to resolve, the project is missing while deliverables claim the milestone, or a resolved sync key contradicts the milestone. Generate no fresh drafts for it and state the exact human action.

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
Record ACTIVE, COMPLETE, or NEEDS_HUMAN_RECONCILIATION per milestone with its Linear project and deliverable issue identifiers.
### Covered deliverables
### Missing deliverables
### Duplicate roadmap keys
### Duplicate sync keys
### Active-ticket conflicts
### Stale draft tickets
### Legacy milestone parent issues
List any issues still carrying `Roadmap sync key: M<number>` that should be canceled after project migration.
### Ambiguities
### Result
Use `READY_TO_SYNC` or `BLOCKED`.

## Milestone Plan

### Milestone ID and outcome
### Completion evidence
### Deliverables
For each deliverable include sync key, title, outcome, acceptance criteria, verification, dependencies, contracts, risks, suggested Linear state, and owning project sync key.
### Integration work
### Release work
### Milestone risks
### Result
Use `READY_TO_SYNC` or `BLOCKED`.

## Linear Milestone Project

### Name
Use `M<number> — milestone name` (same separator and name as the roadmap heading).
### Description
Include roadmap outcome, completion evidence, risks, and exactly one `Roadmap sync key: M<number>` line.
### Team
The configured Linear team from `AGENTS.md`.

## Linear Deliverable Ticket

### Title
### Description
Include outcome, acceptance criteria, verification, contracts, risks, a `Depends on:` line for dependency references, a `Project sync key: M<number>` line, and exactly one `Roadmap sync key: M<number>-D<number>` line.
### Project sync key
The milestone `M<number>` whose Linear project owns this issue.
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
### Created projects
### Created tickets
### Refined tickets
### Unchanged tickets
### Skipped active tickets
### Duplicate roadmap keys
### Duplicate conflicts
### Unsupported mutations
### Stale draft tickets
### Legacy milestone parent issues
### Roadmap link pull request
### Remaining coverage gaps
### Result
Use `SYNCED`, `PARTIAL`, or `BLOCKED`.
