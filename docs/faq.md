# FAQ

## Is Collect affiliated with any catalog site or marketplace?
No. Collect is an independent, vendor-neutral specification. It cross-references existing numbering systems (TCDB, Numista, Scott, Krause...) as `identifiers`, but it doesn't compete with them, replace them, or copy their catalogs — see [architecture.md §6](architecture.md#6-why-cross-reference-instead-of-copying-other-catalogs-numbers). Nothing about the spec requires using, or not using, any particular site or tool.

## Why not just use schema.org or Wikidata?
Both are useful and Collect's [experimental JSON-LD context](../context/collect.jsonld) maps to schema.org and Dublin Core so records can be read as linked data. But neither defines the collectibles-specific layer model (work/catalog/variant/instance/collection), condition grading, rights-aware images, or a CSV mapping that a collector with a spreadsheet can use without knowing what RDF is. Collect is meant to be a practical, JSON-native format collectors and small tools actually write by hand or generate from spreadsheets; linked-data interoperability is a bonus layer on top, not the primary interface. See [architecture.md](architecture.md) for the full reasoning.

## What's the actual difference between `catalog`, `variant`, and `instance`?
- `catalog` — what a publisher/mint/manufacturer put out: "Publisher X's postcard #7421."
- `variant` — a printing/color/error/back difference *of* that catalog item: "#7421, but with a green-ink back instead of black." Always has a `variantOf` pointing at the catalog item.
- `instance` — the physical object you (or someone) actually has: "my copy of #7421, VG, bought for $4.50 at a flea market." Points at a `catalog` or `variant` via `instanceOf` — or, for something not in any catalog, describes itself directly and omits `instanceOf`.

See [architecture.md §2](architecture.md#2-why-separate-the-thing-that-was-made-from-the-thing-you-own) for why they're split up this way, and [schema-reference.md](schema-reference.md#layer-specific-fields) for the exact fields on each.

## How do I describe a postcard (or anything else) that isn't in any catalog?
Write an `instance` record without `instanceOf`, and use the ordinary descriptive fields (`title`, `date`, `agents`, `places`...) plus any profile fields that are allowed on the `instance` layer directly. [`examples/postcard/instance-0043-uncataloged.json`](../examples/postcard/instance-0043-uncataloged.json) is a worked example, and the postcard profile deliberately allows `era`, `format`, `printProcess`, and `stampBox` on `instance` for exactly this reason.

## How do I add a new value to a vocabulary (a new agent role, identifier scheme, condition scale...)?
Open a small pull request adding the term to the relevant file in [`vocab/`](../vocab/) (or a profile's own `vocab/` folder), following [`schema/0.1/vocabulary.schema.json`](../schema/0.1/vocabulary.schema.json)'s shape, then run `collect check-standard` to confirm it's well-formed. See [CONTRIBUTING.md](../CONTRIBUTING.md). Using an unlisted value in a record isn't blocked while you wait for the PR — it's a warning, not an error (see [architecture.md §4](architecture.md#4-why-the-validator-treats-vocabularies-as-open-lists)) — but adding it properly means everyone's tools recognize it too.

## My hobby doesn't have a profile yet. What do I do?
Reuse the core as far as it goes (publishers/artists are `agents`, catalog numbers are `identifiers`, depicted places are `places`), then propose a profile using the "Profile proposal" issue template. See [`spec/profiles.md`](../spec/profiles.md) for the mechanism and guidelines, and the [ROADMAP](../ROADMAP.md) for which profiles are already planned.

## How stable is v0.1? Will my records break in v0.2?
Per [`spec/core.md`](../spec/core.md), the spec is a draft and **may** change before 1.0; breaking changes before 1.0 will be listed in [`CHANGELOG.md`](../CHANGELOG.md). In practice the core is intentionally small and has stayed stable through the postcard profile's development, and the plan (see [ROADMAP.md](../ROADMAP.md)) is to freeze the core well before profile coverage is complete, precisely so early adopters aren't repeatedly migrating records. Profiles version independently of the core and of each other.

## Can a record be in more than one profile / category at once?
A record has one `category`, but nothing stops it from carrying fields from more than one profile namespace if that's meaningful for the item (e.g. an item that's both a `menu` and carries a postal-history field). In practice this hasn't come up yet — if you hit a real case, please open an issue with the concrete example.

## How does Collect handle multiple currencies or historical currency values?
`acquired.price` is `{ amount, currency }` with an ISO 4217 currency code — one price, in whatever currency you paid, per instance. There's no built-in conversion or inflation adjustment; that's a tool-level feature, not a data-format concern.

## Is my purchase price / storage location public if I publish my collection?
Not unless you explicitly choose to include it. `acquired` and `storage` are private-by-default (as is any profile field marked `"private": true`) — see [`spec/core.md` §10](../spec/core.md#10-private-data). This is a convention tools are expected to honor when exporting or publishing, not a technical access restriction on the JSON file itself, so don't share a raw file containing private fields you don't want seen.

## Does the CSV mapping round-trip losslessly?
No, and it's not meant to — JSON (or a package) is the lossless form. CSV drops anything that doesn't fit a flat row (`relationships`, `sources`, `provenance`, collection `entries`, `meta`, full agent detail); `collect json2csv` reports exactly what it dropped on stderr rather than silently losing it. See [`spec/csv.md`](../spec/csv.md) and [architecture.md §8](architecture.md#8-why-csv-is-a-first-class-lossy-mapping-rather-than-an-afterthought).

## Where do I ask a question that isn't here?
[Open an issue](https://github.com/rdnovotni/collect/issues) — vague questions and "does this fit the format?" reports are exactly the useful kind right now, per [CONTRIBUTING.md](../CONTRIBUTING.md).
