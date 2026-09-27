# Changelog

All notable changes to the Collect specification, profiles, and tools are listed here.

## Unreleased

- Added `docs/` (architecture and design rationale, schema reference, CLI reference, getting-started walkthrough, FAQ) and `ROADMAP.md` (the full plan across core spec, profiles, tooling, ecosystem, quality, docs, and governance). No changes to the spec, schema, or tools.
- Added the `sports-card` profile 0.1.0 (`set`, `parallel`, `printRun`, `serialNumber`, `rookie`, `autographType`/`autographInscription`, `relicMaterial`/`relicDescription`) with its own vocabularies and worked examples under `examples/sports-card/`. Player and team stay ordinary core `agents`; the card's position within its set stays the core `number` field.
- Decided the 1.0 freeze criteria (see `ROADMAP.md`'s new "1.0 freeze criteria" section): three stable profiles, a stability window with no breaking core changes, a public conformance suite, a second independent implementation, and every P0 roadmap item closed.
- Added `.github/workflows/release.yml`, a PyPI Trusted Publishing (OIDC) release workflow, and a "Releasing" section in `CONTRIBUTING.md`. Publishing itself still needs a maintainer to register the trusted publisher on PyPI and cut the first tagged release.

## 0.1.0 — draft

- Core record format with five layers: work, catalog, variant, instance, collection.
- EDTF dates, typed agents, identifier cross-references, places, rights-aware images, relationships, sources.
- Pluggable condition scales: `postcard-basic`, `raw-card`, `ten-point`.
- Profile mechanism and the first profile: `postcard` 0.1.0.
- CSV mapping and Frictionless-compatible packages.
- Reference tools: `collect validate`, `check-standard`, `csv2json`, `json2csv`.
