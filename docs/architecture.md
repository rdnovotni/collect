# Architecture and design rationale

This document explains *why* Collect is shaped the way it is: the problem it responds to, the decisions that follow from it, and the alternatives that were considered and rejected. The normative rules live in [`spec/`](../spec/core.md); this is the reasoning behind them.

## 1. The problem

Every hobby that has been collected long enough ends up with the same mess:

- A handful of proprietary catalog sites, each with its own numbering, its own database, and no export worth trusting.
- Collectors' own spreadsheets, one per person, with columns that mean subtly different things from one collector to the next.
- Marketplace listings that describe items well enough to sell them, but not well enough to catalog them.

None of these interoperate. A collector who wants to move from one collection-manager app to another re-types everything. A small independent catalog site that shuts down takes its data with it. There is no equivalent of what GEDCOM did for genealogy — a boring, stable, widely-supported interchange format that lets every tool read what every other tool wrote.

Collect is an attempt at that boring format, scoped to collectibles rather than to any one hobby.

## 2. Why separate "the thing that was made" from "the thing you own"

This is the central design decision, and almost everything else follows from it.

Catalog data (what a publisher printed, what a set contains) and personal collection data (what you own, what you paid, where you keep it) have different owners, different lifecycles, and different sensitivities:

- Catalog data is written once by whoever researches it and is meant to be shared and reused by many collectors.
- Personal data is written by each collector about their own copies and is often private (purchase price, storage location).

Systems that merge the two force an uncomfortable choice: either the catalog is duplicated into every collector's private database (so nobody's data stays in sync, and errors get corrected in one place but not another), or personal data leaks into what's meant to be a shared, public catalog.

Collect's five layers — **work, catalog, variant, instance, collection** — split this cleanly:

```
work        the photograph, independent of any printing
  └─ catalog    a specific published item that used that photograph
       └─ variant   a printing/color/back variation of that item
            └─ instance  the physical copy you own, pointing back up the chain
collection      a named list of references to catalog items or instances
```

A catalog publisher only ever produces `work`, `catalog`, and `variant` records. A collector only ever produces `instance` and `collection` records, referencing catalog data they don't own and don't have to maintain. Neither side needs write access to the other's database, and a collector can point their `instance` records at a totally different catalog (or none at all — `instanceOf` is optional) without changing anything about how they describe what they own.

This mirrors, deliberately, patterns already proven elsewhere: FRBR's *work/expression/manifestation/item* hierarchy in bibliographic cataloging, and the ownership/possession split common in museum collection-management systems. Collect is a narrower, JSON-native version of the same idea, sized for a hobbyist rather than an institution.

**Alternative rejected:** a single flat record type with an `owned` flag. This is what most existing spreadsheet templates and hobby-specific apps do. It's simpler to start with, but it means catalog corrections have to be manually propagated to every owner's record, and it makes "what did a publisher actually print" and "what does this specific person happen to own" inseparable questions — which is exactly the ambiguity that causes the most disagreement in existing collector communities.

## 3. Why a small core plus namespaced profiles, not one big schema

A stamp collector needs perforation and watermark fields. A sports card collector needs parallels, serial numbering, and autograph/relic details. A coin collector needs mint marks and metal composition. None of these mean anything to the others, and a schema that tried to define all of them up front would be enormous, would still be incomplete on day one, and would force every hobby to wait on every other hobby's review before a needed field could ship.

Collect instead defines a small core — the fields every collectible shares regardless of hobby (title, date, agents, places, images, identifiers, condition, acquisition) — and lets each hobby define its own **profile**: a versioned set of additional fields, written as namespaced keys (`postcard:era`, `sports-card:parallel`). A profile is data (a `profile.json` file validated by [`schema/0.1/profile.schema.json`](../schema/0.1/profile.schema.json)), not new code, so adding a hobby doesn't require touching the core schema, the validator, or any other profile.

This is the same shape as XML namespaces, RDF vocabularies, or (closer to home) how OpenAPI and JSON:API let implementations add `x-` extensions — a stable core that doesn't have to anticipate every future need, plus a namespacing convention that keeps extensions from colliding.

**Alternative rejected:** `oneOf` polymorphic schemas per category, or a separate top-level schema per hobby. Either approach makes cross-hobby tooling (a generic validator, a generic collection manager) have to know about every hobby in advance, and makes it hard for a record to combine core fields with profile fields in one flat, spreadsheet-friendly object.

## 4. Why the validator treats vocabularies as open lists

Roles, identifier schemes, condition scales, and profile field values are drawn from JSON files in `vocab/` — but an unlisted value is a **warning**, not an error (see [`spec/core.md` §9](../spec/core.md#9-vocabularies), enforced in [`validate.py`](../src/collect_tools/validate.py)).

A closed enum sounds safer, but it means a new attribution role, a new grading company, or a new identifier scheme literally cannot be recorded until someone edits the vocabulary file and cuts a release — which either blocks real collectors from describing real items, or trains everyone to stuff unmodeled facts into `notes` as free text, which defeats the point of having structured fields at all. Warnings let practice run ahead of the vocabulary, flag the gap for whoever's reviewing the data, and leave a paper trail (a `--strict` run in CI) for closing it later.

Condition **scale membership** is the one exception: once a scale like `postcard-basic` is named, a grade value must be one of that scale's defined terms, because condition grades are meaningless if graders can invent their own labels on the same named scale — the scale's whole job is to be a shared vocabulary that different databases sort and filter by consistently.

## 5. Why EDTF for dates

Collectibles are dated with every degree of certainty at once: a coin has a minted year to the day; a postcard might be datable only to "divided-back era, so 1907–1915"; a photo postcard might be undated and undatable beyond "sometime in the 1900s decade." A plain ISO date forces a guess in all three cases and throws away the honest uncertainty.

The Library of Congress's [Extended Date/Time Format](https://www.loc.gov/standards/datetime/) already solves this with a compact, well-specified grammar — unspecified digits (`190X`), qualifiers (`1906?`, `1906~`, `1906%`), and intervals (`1905/1915`) — and it's already used by archives and libraries, so records that use it are legible outside Collect too. Collect v0.1 implements the commonly-needed subset (see [`spec/core.md` §6](../spec/core.md#6-dates)); the full EDTF Level 2 grammar (sets, seasons) is a candidate for a later minor version if profile authors need it (see [ROADMAP.md](../ROADMAP.md)).

**Alternative rejected:** plain ISO 8601 with a separate `dateUncertain: true` flag. This can express "roughly 1906" but not "sometime in the 1900s" or "between 1905 and 1915," which are extremely common in practice for undated ephemera.

## 6. Why cross-reference instead of copying other catalogs' numbers

Established numbering systems (TCDB, Numista, Scott, Krause, grading-service cert numbers) represent real research and real ongoing curation. Collect does not try to replace or re-host them — a record stores a reference (`{ "scheme": "tcdb", "value": "..." }` in `identifiers`) rather than a copy of their data. This keeps Collect legally uncomplicated (no scraping, no redistribution of someone else's proprietary numbering) and keeps those numbers current, since the reference always points back at the authority for that scheme rather than freezing a snapshot.

## 7. Why images carry a mandatory rights status

Open, redistributable catalog data is one of the project's goals, and image rights are the single most common way an open dataset accidentally becomes non-redistributable. Making `rights.status` required on every image (see [`spec/core.md` §7](../spec/core.md#7-images-and-rights)) forces the question to be answered at the point the image is added, not discovered later when someone tries to redistribute a package and can't tell which images they're allowed to include.

## 8. Why CSV is a first-class, lossy mapping rather than an afterthought

Most collectors' existing records live in spreadsheets, and a format that only speaks JSON will never see that data. [`spec/csv.md`](../spec/csv.md) defines a specific, documented column convention (`agent.<role>`, `condition.<scale>`, `<profile>:<field>`...) so that a spreadsheet a collector already has is a short set of column renames away from valid Collect records, and so that `collect json2csv` can round-trip the common case back out for people who never want to leave a spreadsheet.

The mapping is deliberately, explicitly lossy — relationships, sources, provenance, collection entries, and full agent detail don't fit a flat row, and the converter says so out loud (the `NOTE` lines on `json2csv`) rather than silently dropping data. JSON (or a package) is the lossless form; CSV is a convenience projection of it, not a competing format.

## 9. Why the validator is a three-layer check, not a single JSON Schema

Structural validity (is this a well-formed record) and semantic validity (does this reference point at the right kind of record, is this condition grade valid on the scale it names) are different questions, and they need different failure modes. [`validate.py`](../src/collect_tools/validate.py) runs, in order:

1. **JSON Schema** — structure, required fields, EDTF/id syntax. This alone can't validate profile fields (their schemas aren't known until the profile is loaded) or cross-record references (a single record can't see other records), so it doesn't try to.
2. **Profile fields** — is `postcard:era` a real field on the `postcard` profile, is it allowed on this layer, does its value match the field's own schema.
3. **Vocabularies** — warnings for open lists, errors for closed condition scales (§4 above).
4. **Cross-record references** — duplicate ids, and references that resolve to the wrong layer (`instanceOf` pointing at a `work` instead of a `catalog`/`variant`).

Layering it this way is also what makes `collect check-standard` possible: it reuses the schema-and-profile machinery to validate the standard's *own* profile and vocabulary files, so a broken profile definition is caught the same way a broken record is.

## 10. Non-goals

Being explicit about what Collect is *not* trying to be is part of keeping the core small:

- **Not a catalog.** Collect defines the shape of catalog data; it doesn't host one. (A reference catalog built on Collect is a stated later-stage goal — see [ROADMAP.md](../ROADMAP.md) — but it would be one implementation among many, not part of the standard.)
- **Not a marketplace or pricing format.** `acquired.price` records what *you* paid, not a market valuation.
- **Not a full RDF/linked-data model.** The JSON-LD context ([`context/collect.jsonld`](../context/collect.jsonld)) is explicitly experimental and optional (see [`spec/core.md` §12](../spec/core.md#12-linked-data-experimental)); conformance never requires it.
- **Not trying to model every hobby's fields in the core.** That's what profiles are for (§3).

## Further reading

- [`spec/core.md`](../spec/core.md) — the normative rules referenced throughout this document.
- [Schema reference](schema-reference.md) — every field, in one place.
- [ROADMAP.md](../ROADMAP.md) — what's next, and why.
