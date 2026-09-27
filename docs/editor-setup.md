# Editor setup: autocomplete and inline validation

Every schema file under [`schema/0.1/`](../schema/0.1/) and every profile's
`profile.json` declares `$schema`/`$id`, so JSON-aware editors can already
resolve them today and give you autocomplete and inline errors while
hand-writing records — no separate tool needed.

The `$id`s currently point at `raw.githubusercontent.com/rdnovotni/collect/main/...`,
which tracks this repository's `main` branch rather than a fixed, versioned
URL. That's a known gap (see [`ROADMAP.md` §1](../ROADMAP.md#1-core-spec--schema),
"versioned schema `$id` / stable hosting") to be closed before 1.0 — until
then, editor mappings below will need their URL updated once, not rewritten,
when that happens.

## VS Code

Install the [JSON extension](https://marketplace.visualstudio.com/items?itemName=vscode.json)
(bundled by default), then add to your workspace or user `settings.json`:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["*.collect.json"],
      "url": "https://raw.githubusercontent.com/rdnovotni/collect/main/schema/0.1/record.schema.json"
    }
  ]
}
```

`fileMatch` only glob-matches by filename, not content, so this works best
if you name your record files with a `.collect.json` suffix (e.g.
`my-postcard.collect.json`); otherwise map specific paths instead:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["/my-postcards/*.json"],
      "url": "https://raw.githubusercontent.com/rdnovotni/collect/main/schema/0.1/record.schema.json"
    }
  ]
}
```

This won't validate profile fields (`"postcard:era"` etc.) — those are
checked by `collect validate`, not by VS Code's JSON Schema support, since
which profile applies depends on the record's `category` at runtime.

## IntelliJ / WebStorm / PyCharm

**Preferences → Languages & Frameworks → Schemas and DTDs → JSON Schema
Mappings** → add a mapping: Schema file or URL:
`https://raw.githubusercontent.com/rdnovotni/collect/main/schema/0.1/record.schema.json`,
Schema version: **JSON Schema version 2020-12**, then add a file path
pattern for your record files.

## Everything else

The `check-standard` self-check (`collect check-standard`) already validates
`profile.schema.json` and `vocabulary.schema.json` if you're editing a
profile or vocabulary file directly and want the same editor support — map
those `$id`s the same way.
