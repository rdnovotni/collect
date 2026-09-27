# Changelog

All notable changes to the Collect specification, profiles, and tools are listed here.

## Unreleased

- Added `docs/` (architecture and design rationale, schema reference, CLI reference, getting-started walkthrough, FAQ) and `ROADMAP.md` (the full plan across core spec, profiles, tooling, ecosystem, quality, docs, and governance). No changes to the spec, schema, or tools.

## 0.1.0 — draft

- Core record format with five layers: work, catalog, variant, instance, collection.
- EDTF dates, typed agents, identifier cross-references, places, rights-aware images, relationships, sources.
- Pluggable condition scales: `postcard-basic`, `raw-card`, `ten-point`.
- Profile mechanism and the first profile: `postcard` 0.1.0.
- CSV mapping and Frictionless-compatible packages.
- Reference tools: `collect validate`, `check-standard`, `csv2json`, `json2csv`.
