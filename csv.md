# CSV mapping — v0.1 (draft)

Most collectors keep their records in spreadsheets. This mapping defines one way to write Collect records as CSV so that a spreadsheet can be converted to valid records and back. The reference converter is `collect csv2json` / `collect json2csv`.

CSV is **lossy by design**: it covers what a collector would keep in a spreadsheet. `relationships`, `sources`, `provenance`, collection `entries`, `meta`, and agent details beyond role and name are not represented; `collect json2csv` reports anything it drops.

## Rules

- The first row is the header. Files are UTF-8 (a byte-order mark from Excel is accepted).
- Empty cells mean "no value".
- Cells that hold several values separate them with semicolons: `main street; downtown`.
- `collect` is added automatically on import.
- An unknown column is an error, so typos are not silently ignored.

## Columns

| Column | Becomes |
|---|---|
| `id`, `layer`, `category`, `title`, `description`, `date`, `number`, `work`, `variantOf`, `variantType`, `instanceOf`, `quantity`, `status`, `owner`, `purpose`, `storage`, `notes` | The field of the same name. |
| `tags` | `tags` (semicolon-separated). |
| `agent.<role>` | One agent per name, e.g. `agent.publisher`. |
| `identifier.<scheme>` | One identifier per value, e.g. `identifier.publisher-series`. |
| `place.<role>` | One place per name, e.g. `place.depicted`. |
| `condition.<scale>` | A condition entry, e.g. `condition.postcard-basic` = `VG`. |
| `acquired.date`, `acquired.from`, `acquired.venue`, `acquired.note` | Fields of `acquired`. |
| `acquired.price` + `acquired.currency` | `acquired.price`. Both must be present together. `$` and thousands separators are stripped. |
| `image.<side>` | One image per file path or URL, e.g. `image.front`. |
| `image.rights`, `image.license` | Rights applied to every image in the row. Missing means `unknown`. |
| `<profile>:<field>` | A profile field, e.g. `postcard:era`. Booleans accept true/false, yes/no, y/n, 1/0. |
| `<profile>:<field>.<sub>` | A property of an object-valued profile field, e.g. `postcard:postmark.date`. |

See [`examples/csv/my-postcards.csv`](../examples/csv/my-postcards.csv) for a working example.
