# Collect

**An open data standard for collectibles.**

Collect is a shared format for describing collectibles — postcards, sports and trading cards, coins, stamps, menus, and other ephemera — so that catalogs, collection managers, marketplaces, and archives can exchange data freely and collectors are never locked into one site.

Genealogy has GEDCOM, so a family tree can move between apps. Collectors have nothing like it. Collect aims to be that backbone: a small, stable core with hobby-specific profiles layered on top.

> **Status: v0.1 draft.** The format will change before 1.0. Feedback, questions, and profile proposals are very welcome — please [open an issue](https://github.com/rdnovotni/collect/issues).

## The core idea: layers

Collect separates *the thing that was made* from *the thing you own*:

| Layer | What it describes | Example |
|---|---|---|
| **work** | An image or design, independent of any printing | One harbor photograph a publisher reused on several cards |
| **catalog** | A specific published item | Publisher's card #7421 |
| **variant** | A printing, parallel, error, or back variation | #7421 with a green-ink back |
| **instance** | One physical object someone has | *My* copy of #7421: VG, postmarked 1906, bought for $4.50 |
| **collection** | A list of instances or catalog items | "My postcards", "Want list" |

Catalogs publish works, catalog items and variants. Collectors keep instances and collections that point at them. Neither needs the other's database.

## A record

```json
{
  "collect": "0.1",
  "id": "local:0042",
  "layer": "instance",
  "category": "postcard",
  "instanceOf": "example:catalog/pc7421",
  "condition": [{ "scale": "postcard-basic", "value": "VG" }],
  "acquired": { "date": "2026-08", "price": { "amount": 4.5, "currency": "USD" } },
  "postcard:posted": true,
  "postcard:postmark": { "date": "1906-07-14", "place": "Brooklyn, N.Y." }
}
```

Highlights of the design:

- **Uncertain dates** use the Library of Congress EDTF format: `190X`, `1906~`, `1905/1915`.
- **Every image carries a rights status**, so open catalogs stay safely redistributable.
- **Other catalogs' numbers are cross-referenced**, not copied: `{ "scheme": "tcdb", "value": "..." }`.
- **Condition scales are pluggable**: `postcard-basic`, `raw-card`, `ten-point`, or your own.
- **Spreadsheets are first-class**: a defined CSV mapping converts in both directions.

## Repository layout

```
spec/        The specification (start with spec/core.md)
schema/      JSON Schemas for records, profiles and vocabularies
profiles/    Category profiles (postcard is the first)
vocab/       Shared vocabularies: roles, schemes, statuses, condition scales
context/     Experimental JSON-LD context for linked-data use
examples/    Example records, a package, and a CSV
src/         Reference tools (the `collect` command)
tests/       Test suite, including deliberately invalid records
```

## Tools

The reference tools require Python 3.10+.

```bash
pip install -e ".[dev]"

collect validate examples/postcard          # validate records, files, or packages
collect csv2json my-postcards.csv -o my-postcards.json
collect json2csv examples/postcard -o out.csv
collect check-standard                      # validate the profiles and vocabularies themselves
pytest                                      # run the tests
```

The validator checks structure, dates, profile fields, condition grades, and references between records (for example, that `instanceOf` points at a catalog item and not a work). Unknown vocabulary terms are warnings, not errors; use `--strict` to treat them as errors.

## Roadmap

- **v0.1** — Core schema, postcard profile, CSV mapping, packages, validator *(this release)*
- **v0.2** — Sports card profile; importers for spreadsheet exports from existing card and coin sites
- **v0.3** — A simple reference collection manager, then an open postcard catalog built on Collect

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The most useful contributions right now are real-world records that don't fit the format, and profile proposals from people who know a hobby well.

## License

- Specification and documentation: [CC BY 4.0](LICENSE-SPEC)
- Code: [MIT](LICENSE)
- Vocabularies and examples: [CC0 1.0](LICENSE-DATA)
