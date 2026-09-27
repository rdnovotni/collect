# Packages — v0.1 (draft)

A **package** bundles many records, and optionally their images, for publishing or moving a whole catalog or collection. Collect packages are [Frictionless Data Packages](https://specs.frictionlessdata.io/data-package/), so general-purpose data tools can already read them.

## Layout

```
my-package/
├── datapackage.json      manifest
├── records.jsonl         one Collect record per line
└── images/               image files referenced by records (optional)
```

A package may also be distributed as a `.zip` of this folder.

## Manifest

```json
{
  "name": "example-postcards",
  "title": "Example postcard package",
  "licenses": [{ "name": "CC0-1.0", "path": "https://creativecommons.org/publicdomain/zero/1.0/" }],
  "collect": {
    "version": "0.1",
    "profiles": ["postcard@0.1.0"],
    "prefixes": { "example": "https://example.org/collect/" }
  },
  "resources": [
    { "name": "records", "path": "records.jsonl", "format": "jsonl", "mediatype": "application/x-ndjson" }
  ]
}
```

- `collect.version` — the core version the records follow.
- `collect.profiles` — profiles used, as `id@version`.
- `collect.prefixes` — what each id prefix expands to, so `example:catalog/pc7421` can be read as `https://example.org/collect/catalog/pc7421`.
- Resources may be `.jsonl` files or `.json` files holding one record or an array.

`collect validate my-package/` validates every record in the package and checks references between them. Image paths in records are relative to the package root.

Packages that contain personal collection data should follow the private-data guidance in [core.md §10](core.md#10-private-data).
