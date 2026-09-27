# Getting started

A hands-on walkthrough: install the tools, write a record, validate it, and convert it to and from CSV. Takes about five minutes. For the concepts behind each step, see [architecture.md](architecture.md); for every field available, see [schema-reference.md](schema-reference.md).

## 1. Install

Requires Python 3.10+.

```bash
git clone https://github.com/rdnovotni/collect.git
cd collect
pip install -e ".[dev]"
collect --version
```

## 2. Look at a real example first

The repository ships a small, connected set of example records under [`examples/postcard/`](../examples/postcard/): a `work`, two `catalog` items that reuse it, a `variant`, an `instance` someone owns, and two `collection` lists. Validate them:

```bash
collect validate examples/postcard
```

```
9 record(s): 0 error(s), 0 warning(s)
```

Open [`examples/postcard/instance-0042.json`](../examples/postcard/instance-0042.json) alongside [`examples/postcard/catalog-pc7421.json`](../examples/postcard/catalog-pc7421.json) — the instance's `instanceOf` points at the catalog item's `id`. That link is what `collect validate` checks.

## 3. Write your own record

Not every postcard you own is in a catalog. Here's a minimal `instance` record for one that isn't — it just describes itself directly, using core fields plus two `postcard:` profile fields:

```json
{
  "collect": "0.1",
  "id": "local:0100",
  "layer": "instance",
  "category": "postcard",
  "title": "Lighthouse at dusk",
  "date": "1915/1925",
  "status": "owned",
  "condition": [{ "scale": "postcard-basic", "value": "EX" }],
  "postcard:posted": false,
  "notes": "No publisher mark; picked up at an estate sale."
}
```

Save it as `my-postcard.json` and validate it:

```bash
collect validate my-postcard.json
```

```
1 record(s): 0 error(s), 0 warning(s)
```

Try breaking it to see the validator's messages — an invalid condition grade:

```bash
sed -i 's/"EX"/"VF"/' my-postcard.json
collect validate my-postcard.json
```

```
ERROR   my-postcard.json [local:0100] at $.condition[0].value: 'VF' is not a grade on the 'postcard-basic' scale
1 record(s): 1 error(s), 0 warning(s)
```

`postcard-basic` only knows `M, NM, EX, VG, G, F, P` — `VF` isn't one of them (that's a `raw-card`/`ten-point` grade). Undo the edit before continuing.

## 4. Add it to a collection

A `collection` record is a named list of references:

```json
{
  "collect": "0.1",
  "id": "local:collections/my-postcards",
  "layer": "collection",
  "title": "My postcards",
  "purpose": "have",
  "entries": [{ "ref": "local:0100" }]
}
```

Save it as `my-collection.json` and validate both files together, so the reference can resolve:

```bash
collect validate my-postcard.json my-collection.json
```

```
2 record(s): 0 error(s), 0 warning(s)
```

Validating `my-collection.json` on its own would produce a warning — `reference 'local:0100' not found in the records checked` — because the validator only resolves references within the set of paths given on one command line. This is deliberate: it's how the same tool validates one file in isolation and a whole multi-file collection together.

## 5. Spreadsheets: CSV in and out

If you'd rather keep records in a spreadsheet, see [`spec/csv.md`](../spec/csv.md) for the column convention (a working example is [`examples/csv/my-postcards.csv`](../examples/csv/my-postcards.csv)), then convert:

```bash
collect csv2json examples/csv/my-postcards.csv -o my-postcards.json
collect validate my-postcards.json
```

And back out — this direction is lossy, and the converter says exactly what it dropped:

```bash
collect json2csv examples/postcard -o out.csv
```

```
NOTE    example:catalog/pc7421: 'relationships' not representable in CSV
NOTE    local:collections/postcards: 'entries' not representable in CSV
...
```

## 6. Packaging a set of records

To bundle many records (and their images) for publishing or moving a whole catalog, see [`spec/packages.md`](../spec/packages.md) and the worked example in [`examples/package/`](../examples/package/):

```bash
collect validate examples/package
```

## Next steps

- [Schema reference](schema-reference.md) — every field, on every layer.
- [`spec/profiles.md`](../spec/profiles.md) — write a profile for a hobby that doesn't have one yet.
- [CLI reference](cli-reference.md) — every flag and exit code.
- [FAQ](faq.md) — common questions.
- [CONTRIBUTING.md](../CONTRIBUTING.md) — the most useful contribution right now is a real record that doesn't fit the format.
