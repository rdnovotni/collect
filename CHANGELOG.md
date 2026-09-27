# Changelog

All notable changes to the Collect specification, profiles, and tools are listed here.

## Unreleased

- Closed the rest of the roadmap's P1 items: a "Decision process" section in `CONTRIBUTING.md`; concrete `local:` id-merge guidance in `spec/core.md` §4.1; Dependabot plus a `pip-audit` CI step; property-based (Hypothesis) EDTF tests; a public, implementation-agnostic conformance suite (`conformance/v0.1/`); a `--format sarif` validator output; the `collect init` scaffold command; the `coin` and `stamp` profiles (plus the shared `sheldon-70` condition scale); and JSON Schema editor setup docs. The EDTF Level 2 subset and the browser-based validator stay open in `ROADMAP.md` — the former still has no concrete profile trigger, the latter is still blocked on the JS/TS validator port.
- Added a `mkdocs`-based project website (`mkdocs.yml`, the `docs` extra, `.github/workflows/docs.yml`) rendering `docs/`, `spec/`, and a generated schema/profile browser. The workflow is ready but not yet live — a maintainer still needs to enable GitHub Pages ("Build and deployment: GitHub Actions") once.
- Added `docs/` (architecture and design rationale, schema reference, CLI reference, getting-started walkthrough, FAQ) and `ROADMAP.md` (the full plan across core spec, profiles, tooling, ecosystem, quality, docs, and governance). No changes to the spec, schema, or tools.
- Added the `sports-card` profile 0.1.0 (`set`, `parallel`, `printRun`, `serialNumber`, `rookie`, `autographType`/`autographInscription`, `relicMaterial`/`relicDescription`) with its own vocabularies and worked examples under `examples/sports-card/`. Player and team stay ordinary core `agents`; the card's position within its set stays the core `number` field.
- Decided the 1.0 freeze criteria (see `ROADMAP.md`'s new "1.0 freeze criteria" section): three stable profiles, a stability window with no breaking core changes, a public conformance suite, a second independent implementation, and every P0 roadmap item closed.
- Added `.github/workflows/release.yml`, a PyPI Trusted Publishing (OIDC) release workflow, and a "Releasing" section in `CONTRIBUTING.md`. Publishing itself still needs a maintainer to register the trusted publisher on PyPI and cut the first tagged release.
- Bumped `collect_tools.__version__` past the `0.1.0.dev0` placeholder to `0.1.0`, clearing the last code-side blocker on the PyPI release roadmap item.
- Closed the remaining gaps in `pytest` coverage of the `check-standard`/`validate` code paths (`validate.py` is now fully covered; `cli.py`'s `validate`/`check-standard`/`--format json` paths and error handling are too), with new fixtures for malformed records, unknown profile prefixes, invalid `layer`/condition-scale values, and a broken standalone data root exercising `check_standard()`'s own error-reporting branches.

## 0.1.0 — draft

- Core record format with five layers: work, catalog, variant, instance, collection.
- EDTF dates, typed agents, identifier cross-references, places, rights-aware images, relationships, sources.
- Pluggable condition scales: `postcard-basic`, `raw-card`, `ten-point`.
- Profile mechanism and the first profile: `postcard` 0.1.0.
- CSV mapping and Frictionless-compatible packages.
- Reference tools: `collect validate`, `check-standard`, `csv2json`, `json2csv`.
