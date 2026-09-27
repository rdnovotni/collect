# Roadmap

Where Collect is going, organized by theme, and roughly ordered within each theme. This expands on the short version in [README.md](README.md#roadmap). It's a living planning document, not a commitment with dates — see [CONTRIBUTING.md](CONTRIBUTING.md) for how to help move any of it forward, and open an issue to propose changes to it.

Priority tags: **P0** blocks the next release or is actively needed now. **P1** clearly next. **P2** valuable but not urgent. **P3** long-term / exploratory.

## Guiding goal

Genealogy has GEDCOM. Collect aims to be the same thing for collectibles: boring, stable, and widely supported enough that no collector is ever locked into one tool, and no small catalog site's shutdown takes its data down with it. Every item below is in service of that — either making the core trustworthy enough to build on, or making it easy enough to adopt that people actually do.

## Release milestones

- **v0.1 (current)** — Core schema (5 layers), postcard and sports-card profiles, CSV mapping, packages, reference validator and CLI, CI, issue/PR templates.
- **v0.2 (next)** — First real-world importer(s) from existing spreadsheet/export formats; `collect-tools` on PyPI; core-freeze candidate.
- **v0.3** — A simple reference collection manager; groundwork for an open, community-run postcard catalog built on Collect.
- **v1.0** — Core spec frozen and versioned for real, against the criteria below; conformance test suite; multiple independent implementations exist.

## 1.0 freeze criteria

"Ready for 1.0" means all of the following hold at once, not just at some point in the past:

1. **At least three profiles at `status: stable`** (not `draft`) — postcard and sports-card plus one more (§2) — so the profile mechanism is proven outside its original use case.
2. **No breaking core-schema change** (`schema/0.1/*.schema.json` or `spec/core.md`'s normative rules) **for two consecutive minor spec releases**, so implementers aren't targeting a moving floor.
3. **A public, versioned, implementation-agnostic conformance test suite** exists (§4) — not just this repo's `pytest` fixtures.
4. **A second independent implementation** (any language) passes that conformance suite.
5. **All P0 items across every section of this roadmap are closed.**

Until all five hold, the spec stays "draft" — see [`spec/core.md`](spec/core.md) — and any of them may still change core behavior.

## 1. Core spec & schema

- **P1 — EDTF Level 2 subset, if a profile needs it.** Seasons, sets of dates (`[1667,1668,1670]`), and qualified individual date-parts aren't in v0.1's subset (see [`spec/core.md` §6](spec/core.md#6-dates)). Add only when a concrete profile needs one of these, so the grammar doesn't grow speculatively. Reconsidered when adding the `coin` and `stamp` profiles (§2) — neither needed it, so it's still deferred.
- **P2 — Multi-part / composite items.** Sets that ship as one physical unit (a boxed set, a booklet of stamps, a multi-card insert) don't yet have a clean modeling story distinct from a `collection`. Needs a concrete failure case from real data before designing further, per the project's own contribution priorities.
- **P2 — Non-USD-centric price modeling for historical/foreign currency.** Current `price` (`amount` + ISO 4217 `currency`) covers the common case; revisit only if real records surface a gap (pre-decimal currencies, tokens, barter).
- **P3 — Versioned schema `$id` / stable hosting.** Schema `$id`s currently point at `raw.githubusercontent.com/.../main/...`, which moves with the default branch. Before 1.0, decide on stable, version-pinned URLs (e.g. a project domain or a tagged-release raw URL) so external tools can depend on a schema URL that won't change under them.

## 2. Profiles

- **P2 — `trading-card` / `non-sport-card`** (already in `vocab/categories.json`), **`comic`**, **`vinyl-record`**, **`banknote`**, **`ticket`/`program`**. Prioritize by contributor interest — a profile needs a domain expert willing to shape it, not just a category slug that already exists.
- **P2 — A profile author's checklist / template.** A short worked template (folder skeleton, a minimal `profile.json`, a first vocab file, a first example record) so proposing a new profile is closer to "fill in this template" than "read the spec and figure it out."
- **P3 — Cross-profile shared sub-vocabularies.** Once 3+ profiles exist, look for fields that turned out not to be hobby-specific after all (e.g. a grading-company list used by both `sports-card` and `coin`) and promote them to `vocab/` if they're genuinely shared.

## 3. Tooling & developer experience

- **P0 — Ship `collect-tools` to PyPI.** It's currently install-from-source only (`pip install -e ".[dev]"`); a tagged PyPI release is the difference between "clone the repo" and "pip install" for every downstream tool and profile author. The release workflow ([`.github/workflows/release.yml`](.github/workflows/release.yml)) is in place, using PyPI's Trusted Publishing (OIDC, no stored API token) triggered on a GitHub Release, and the version in [`src/collect_tools/__init__.py`](src/collect_tools/__init__.py) is past the `.dev0` placeholder (`0.1.0`); what's left is a maintainer creating the `collect-tools` project on PyPI, registering this workflow as its trusted publisher, and cutting the first tagged release — all of which require PyPI/GitHub release access this repo's automation doesn't have.
- **P2 — Importers from existing formats.** Read exports from popular collection-manager apps and spreadsheet templates already in use in postcard/sports-card communities, and convert to Collect records — this is explicitly called out in the v0.2 milestone and is the fastest path to real adoption evidence.
- **P2 — Language ports.** A minimal validator (schema + profile + reference checks) in JS/TS (for browser and Node tooling) and one more ecosystem (Go or Rust) would prove the spec isn't accidentally Python-shaped, and unblock web-based tools (§4).
- **P3 — `collect diff` / `collect merge`.** Comparing two versions of a record or package, and merging edits from two contributors to the same catalog — useful once multiple people co-maintain one open catalog.

## 4. Ecosystem & interoperability

- **P1 — A minimal browser-based validator.** A static page that runs schema + profile validation client-side (once a JS/TS implementation exists, §3) so someone can paste or drop a record and get feedback with no install — the lowest-friction way for a skeptical collector to try the format. Still blocked on that JS/TS port (§3), which hasn't started; there's nothing to build client-side yet without hand-duplicating the Python validator's logic in JS, which would drift immediately.
- **P2 — A reference collection manager** (the v0.3 milestone). Deliberately simple: import/export Collect records, browse a collection, edit records through a form rather than raw JSON. Its job is to prove the format is usable end-to-end for someone who will never open a text editor, not to compete with full-featured commercial tools.
- **P2 — An open, community-run postcard catalog built on Collect** (also v0.3). Depends on the reference collection manager and on real profile stability; the first place the "catalogs publish, collectors reference" split (see [architecture.md §2](docs/architecture.md#2-why-separate-the-thing-that-was-made-from-the-thing-you-own)) gets exercised for real instead of in examples.
- **P3 — Outreach to existing catalog sites and marketplaces.** Once there's at least one working importer/exporter and a stable core, approach maintainers of existing hobby databases about publishing (or accepting) a Collect export — this only becomes a credible ask after §3/§4's tooling exists, not before.
- **P3 — Linked-data maturity.** Expand [`context/collect.jsonld`](context/collect.jsonld) and consider a SHACL shape alongside the JSON Schema, keeping it explicitly optional per [`spec/core.md` §12](spec/core.md#12-linked-data-experimental) — this stays low priority until core adoption exists to link data *between*.

## 5. Quality, testing & security

- **P0 — Keep 100% of `check-standard`/`validate` paths covered by `pytest`.** Already true today (all tests green, including both profiles' examples) — the goal is to keep any new validator behavior landing with a fixture in `tests/fixtures`, not just an example that happens to pass.
- **P2 — Large-package performance.** `collect validate` currently loads everything into memory; before packages reach real-catalog scale (thousands of records with images), profile it and consider streaming validation for `.jsonl` packages.
- **P2 — A security/privacy review of the private-data convention.** §10 of the core spec is a *convention* tools should honor, not an enforced access control — document this gap explicitly somewhere prominent (it's already implicit in `spec/core.md`, but a contributor building a "publish my collection" tool should not be able to miss it) and consider whether the validator should warn when a record with private fields is being emitted from a `--publish`-style tool command in the future.

## 6. Documentation & website

- **P2 — A visual diagram of the layer model** (work → catalog → variant → instance, collection alongside) for the README and website — the concept is simple once seen, and currently only exists as the table in [README.md](README.md#the-core-idea-layers).
- **P3 — Translations of the spec.** Not urgent while the spec itself is still changing pre-1.0 (translations would need re-syncing on every change), but worth planning for once the core freezes.

## 7. Governance & community

- **P2 — A place to discuss that isn't just GitHub issues.** As profile count and contributor count grow, a lower-friction space (Discussions tab, or a small forum/Discord) for "does this fit the format?" questions that aren't yet issue-shaped would match how [CONTRIBUTING.md](CONTRIBUTING.md) already says the most valuable contributions are — informal reports of real items that don't fit.
- **P3 — A steering/maintainers group.** Only once there's more than one active maintainer and more than one organization depending on the spec — premature before then.

## How this roadmap gets updated

When a milestone ships, move its items into [`CHANGELOG.md`](CHANGELOG.md) and delete or re-scope them here rather than letting both documents describe the same finished work. When priorities change, edit this file directly and mention why in the pull request — the roadmap should reflect current thinking, not the order things were first written down in.
