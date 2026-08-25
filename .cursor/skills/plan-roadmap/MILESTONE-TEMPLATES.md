# Roadmap Planning Templates

Use every heading. Write `None` when a non-verdict section has no entries.

## Stable identifiers

Roadmap milestone headings use:

`## M<number> — milestone name`

Roadmap deliverables use:

`- [M<number>-D<number>] deliverable outcome`

Every synced Linear issue description contains:

`Roadmap sync key: M<number>` for a milestone parent.

`Roadmap sync key: M<number>-D<number>` for a deliverable.

Sync keys are immutable. A renamed outcome keeps its existing key.

## Roadmap Coverage Report

### Approved roadmap SHA
### Milestones inspected
### Covered deliverables
### Missing deliverables
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
Include roadmap outcome, completion evidence, risks, and `Roadmap sync key: M<number>`.
### State
Use `Draft` or `Needs Planning`.

## Linear Deliverable Ticket

### Title
### Description
Include outcome, acceptance criteria, verification, contracts, risks, dependencies, and `Roadmap sync key: M<number>-D<number>`.
### Parent sync key
### Dependency sync keys
### State
Use `Draft` or `Needs Planning`.

## Reconciliation Report

### Approved roadmap SHA
### Linear pagination proof
### Relation mutation schema proof
### Created tickets
### Refined tickets
### Unchanged tickets
### Skipped active tickets
### Duplicate conflicts
### Unsupported mutations
### Stale draft tickets
### Remaining coverage gaps
### Result
Use `SYNCED`, `PARTIAL`, or `BLOCKED`.
