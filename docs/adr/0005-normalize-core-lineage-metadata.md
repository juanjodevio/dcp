# Normalize core lineage metadata

Status: Accepted
Date: 2026-08-25

## Context And Problem Statement

How should dbt artifact data be stored so lineage UI is responsive without coupling Postgres to the full evolving dbt artifact schema?

## Decision Drivers

- Responsive lineage UI
- Avoid reimplementing dbt artifact schemas in SQL
- Keep raw evidence for drill-down and debugging

## Considered Options

- Normalize core lineage (nodes/edges) in Postgres; raw artifacts in object storage
- Normalize entire manifest/run_results into Postgres
- Object storage only; Postgres holds run row metadata only

## Decision Outcome

Chosen option: "Normalize core, lazy-load rest". Store run metadata, artifact index, and model/source/test lineage edges in PostgreSQL. Keep full `manifest.json`, `run_results.json`, logs, and Elementary payloads in object storage.

## Consequences

- Good, because lineage queries stay fast and scoped
- Bad, because ingestion must carefully choose which fields to normalize as dbt versions change
- Good, because raw artifacts remain canonical for deep inspection

## Confirmation

Lineage API/UI reads Postgres edges; artifact download paths hit object storage; no requirement that full manifest columns exist in SQL.

## More Information

- `docs/PRODUCT.md`
- MVP design spec artifact section
