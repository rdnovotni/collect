# Collect Core Specification — v0.1 (draft)

**Status:** Draft. Anything may change before 1.0. Feedback is welcome through issues.
**License:** [CC BY 4.0](../LICENSE-SPEC)

The key words MUST, SHOULD and MAY are used as described in RFC 2119.

## 1. Purpose

Collect is a shared format for describing collectibles — postcards, cards, coins, stamps, ephemera, anything mass-produced and collected — so that catalogs, personal collection tools, marketplaces and archives can exchange data without losing meaning or locking collectors in.

Collect is not a catalog. It defines how catalog and collection data is shaped, so that anyone can publish a catalog, and any collector can move their records between tools.

## 2. Design principles

1. **Separate the thing that was made from the thing you own.** Catalog data and personal data live in different layers and link together.
2. **Small core, extensible profiles.** The core covers what every collectible shares. Hobby-specific detail lives in profiles.
3. **Honest uncertainty.** Dates, attributions and identifications are often uncertain, and the format must say so rather than force a guess.
4. **Rights-aware.** Every image carries a rights status so open catalogs stay safely redistributable.
5. **Cross-reference, don't copy.** Proprietary numbering systems can be referenced by number without reproducing their catalogs.
6. **Spreadsheet-friendly.** A defined CSV mapping (see [csv.md](csv.md)) keeps the standard usable by collectors who never touch JSON.

## 3. Records and layers

A Collect document is a JSON object called a **record**. Every record MUST have:

| Field | Meaning |
|---|---|
| `collect` | The spec version, `"0.1"`. |
| `id` | A unique identifier (see §4). |
| `layer` | One of `work`, `catalog`, `variant`, `instance`, `collection`. |

The five layers:

- **work** — The abstract design or image, independent of any printing. When a publisher reuses one photograph across several cards — cropped, mirrored, recolored — those cards share one work. Works are optional.
- **catalog** — A specific published item: a postcard in a publisher's series, a card in a set, a coin type. Sets and series are themselves catalog records; items link to them with a `part-of` relationship and MAY give their position in `number`. A catalog record MAY name its work in `work`.
- **variant** — A printing, parallel, error, color, back or size variation of a catalog item. MUST name its parent in `variantOf`; SHOULD give a `variantType`.
- **instance** — One physical object that someone has. SHOULD name what it is in `instanceOf` (a catalog or variant record). An instance of something not in any catalog MAY omit `instanceOf` and describe itself with the ordinary descriptive fields.
- **collection** — A named list (`entries`) of references: a collection, want list, trade list or checklist, with an optional `purpose`.

References between layers MUST point at the right kind of record: `instanceOf` → catalog or variant; `variantOf` → catalog; `work` → work.

## 4. Identifiers

An `id` is either an absolute URI or a compact identifier `prefix:path`, such as `example:catalog/pc7421`.

- A catalog publisher SHOULD choose a short, stable prefix and declare what it expands to in a package manifest (see [packages.md](packages.md)).
- The prefix `local:` is reserved for records that are only meaningful inside one person's collection (`local:0042`). Tools MUST NOT assume `local:` ids are unique across collections.
- Once published, catalog ids SHOULD NOT change. Replace a record by publishing a new one with a `replaces` relationship.

### 4.1. Merging `local:` records from two collections

A tool that combines two people's collections (or imports one person's export into another's) MUST NOT assume their `local:` ids refer to different things just because the strings differ, nor that two records sharing a `local:` id are the same thing. Concretely:

- **Detect** a collision only when two records' `local:` ids are the literal same string; two different `local:` ids are never assumed to collide, and are never assumed to be duplicates of each other either.
- **Remap, don't overwrite.** When merging into one dataset, generate a fresh id for every incoming record whose `local:` id already exists in the target (or simply re-mint every incoming `local:` id to guarantee no collision), and rewrite every reference to the old id within the same merge — `instanceOf`, `variantOf`, `work`, `relationships[].target`, and collection `entries[].ref` — so the merged dataset stays internally consistent. Never silently drop or overwrite one side's record because its id matched the other's.
- **Prefer promoting to a stable prefix over remapping within `local:`.** If the merge is really a publication step (one collector's records becoming part of a shared catalog), assigning the records a real, stable prefix per §4 is usually the better fix than perpetuating `local:` ids across collections.
- Tools SHOULD keep a record of the remapping (old id → new id) for the duration of the merge so any external references the user holds (e.g. in a collection list they didn't include in this merge) can be updated too.

External numbering systems go in `identifiers`, as `{ "scheme": ..., "value": ... }` pairs, never in `id`. Recording another scheme's number is a cross-reference; it does not make the record part of that scheme's catalog.

## 5. Descriptive fields (all layers)

| Field | Type | Notes |
|---|---|---|
| `category` | term | See `vocab/categories.json`. Usually matches a profile. |
| `title`, `description` | text | |
| `date` | EDTF | See §6. |
| `agents` | list | `{ role, name, id?, identifiers?, note? }`. Roles: `vocab/agent-roles.json`. |
| `identifiers` | list | `{ scheme, value, note? }`. Schemes: `vocab/identifier-schemes.json`. |
| `places` | list | `{ role?, name, wikidata?, geonames?, lat?, lon?, note? }`. Role defaults to `depicted`. |
| `images` | list | `{ file or url, side?, caption?, rights }`. See §7. |
| `relationships` | list | `{ type, target, note? }`. Types: `vocab/relationship-types.json`. |
| `sources` | list | Where the information came from: `{ title?, url?, citation?, contributor?, date?, note? }`. |
| `tags` | list | Free-text tags. |
| `notes` | text | |
| `meta` | object | About the record, not the object: `created`, `modified`, `license`, `contributors`. |

Instance records add `quantity`, `status`, `condition`, `acquired`, `provenance` and `storage`. Condition entries are `{ scale, value, grader?, certNumber?, date?, note? }`, where `scale` names a file in `vocab/condition-scales/`. A value that is not on a known scale is an error.

Any other top-level key MUST be a profile field (§8). Unknown plain keys are errors, which catches typos.

## 6. Dates

`date` fields use the Library of Congress **Extended Date/Time Format (EDTF)**. Collect v0.1 accepts this subset:

| Form | Example | Meaning |
|---|---|---|
| Year, month, day | `1906`, `1906-07`, `1906-07-14` | |
| Unspecified digits | `190X`, `19XX`, `1906-XX` | Sometime in the 1900s decade, etc. |
| Uncertain / approximate | `1906?`, `1906~`, `1906%` | Possibly 1906 / about 1906 / both. |
| Interval | `1905/1915`, `1907/..`, `../1915` | Between; open-ended. |

"Circa 1905" is written `1905~`. A card known only by its era is better written as an interval (`1907/1915`) than as a guessed year.

## 7. Images and rights

Every image MUST have `rights.status` from `vocab/rights-statuses.json`: `public-domain`, `licensed` (which MUST then give an SPDX `license` id), `permission-granted`, `all-rights-reserved` or `unknown`.

Tools that publish open catalogs SHOULD exclude images whose status is `all-rights-reserved` or `unknown`.

## 8. Profiles

Profiles add category-specific fields, used as namespaced keys: `"postcard:era": "divided-back"`. Each profile field declares which layers it may appear on, a JSON Schema for its value, and optionally a vocabulary. See [profiles.md](profiles.md).

## 9. Vocabularies

Vocabularies (roles, schemes, statuses, scales) are open lists. An unlisted value is a **warning**, not an error, so new practice can appear before the vocabulary catches up. Additions are proposed through the normal contribution process.

## 10. Private data

`acquired`, `storage`, and profile fields marked `"private": true` hold personal information such as prices paid and storage locations. Tools SHOULD leave these out of anything they publish or share unless the owner explicitly includes them.

## 11. Conformance

A record conforms to Collect v0.1 when it validates against `schema/0.1/record.schema.json` and its profile fields validate against their profiles. The reference validator (`collect validate`) performs these checks and also verifies references between records.

## 12. Linked data (experimental)

`context/collect.jsonld` maps core terms to schema.org and Dublin Core, so records can be read as JSON-LD. It is optional and not needed for conformance.
