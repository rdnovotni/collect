# CLI reference

The reference implementation ships a single command, `collect`, with four subcommands. Source: [`src/collect_tools/cli.py`](../src/collect_tools/cli.py). Install with `pip install -e ".[dev]"` (Python 3.10+).

```
collect --version
collect <command> [options]
```

## `collect validate`

```
collect validate <path> [<path> ...] [--strict] [--format text|json]
```

Validates records against the core schema, their profile(s), the standard's vocabularies, and cross-record references (see [architecture.md §9](architecture.md#9-why-the-validator-is-a-three-layer-check-not-a-single-json-schema)).

**Arguments**

- `<path>` (one or more) — a `.json` file (one record or an array of records), a `.jsonl` file (one record per line), a directory (scanned recursively for `.json`/`.jsonl` files), or a package directory (one containing `datapackage.json`).

**How paths are grouped for cross-referencing:** each package directory (one with a `datapackage.json`) is validated as its own self-contained dataset — references only resolve against records in that same package. Every other path given in the same invocation is pooled into one combined dataset, so a reference in one file can resolve against a record in another file on the same command line. Pass a package and loose files together to validate both; they won't cross-reference each other.

**Options**

| Flag | Effect |
|---|---|
| `--strict` | Treat warnings as errors (affects the exit code, not what's printed). |
| `--format text\|json` | `text` (default) prints one line per issue plus a summary; `json` prints a JSON array of issue objects (see below) and suppresses the summary line. |

**Exit codes:** `0` no errors (and, with `--strict`, no warnings); `1` errors found (or warnings, under `--strict`); `2` a path could not be read (bad JSON, missing file).

**Examples**

```bash
collect validate examples/postcard
collect validate examples/postcard examples/package
collect validate my-collection/ --strict
collect validate my-collection/ --format json > report.json
```

## `collect check-standard`

```
collect check-standard [--strict] [--format text|json]
```

Validates the standard's *own* files — every `profiles/*/*/profile.json` against `schema/0.1/profile.schema.json` (plus that each field's own `schema` is itself a valid JSON Schema, and that any `vocabulary` path it names actually exists), and every file under `vocab/` and each profile's `vocab/` folder against `schema/0.1/vocabulary.schema.json` (plus duplicate-term-id detection). Run this after editing a profile or vocabulary, before running `collect validate` against records that use it.

Same `--strict` / `--format` / exit-code behavior as `validate`.

## `collect csv2json`

```
collect csv2json <input.csv> [-o <output>] [--jsonl]
```

Converts a CSV spreadsheet (see [`spec/csv.md`](../spec/csv.md) for the column mapping) into Collect records. Reads UTF-8, including a BOM from Excel.

| Flag | Effect |
|---|---|
| `-o, --output <path>` | Write to a file instead of stdout. |
| `--jsonl` | Write one JSON object per line instead of a single indented JSON array. |

An unknown column, or a malformed value the mapping can't parse, is a `CsvError` — the command prints it to stderr and exits `1`.

```bash
collect csv2json my-postcards.csv -o my-postcards.json
collect csv2json my-postcards.csv --jsonl -o my-postcards.jsonl
```

## `collect json2csv`

```
collect json2csv <input> [<input> ...] [-o <output>]
```

Flattens Collect records (from any of the path forms `validate` accepts) into one CSV. This mapping is **lossy by design** — see [`spec/csv.md`](../spec/csv.md) and [architecture.md §8](architecture.md#8-why-csv-is-a-first-class-lossy-mapping-rather-than-an-afterthought). Anything dropped (`relationships`, `sources`, `provenance`, collection `entries`, `meta`, agent detail beyond role and name) is reported as a `NOTE` line on stderr, one per record/field combination — the command still exits `0`, since dropping unmappable fields on this lossy path is expected, not an error.

```bash
collect json2csv examples/postcard -o out.csv
collect json2csv examples/postcard examples/package -o out.csv
```

## Issue objects (`--format json`)

Both `validate` and `check-standard` can emit issues as JSON — useful for feeding a CI annotation step or a different report format. Each issue:

```json
{
  "level": "error",
  "location": "examples/postcard/instance-0042.json",
  "record": "local:0042",
  "path": "$.condition[0].value",
  "message": "'VF' is not a grade on the 'postcard-basic' scale"
}
```

| Field | Meaning |
|---|---|
| `level` | `"error"` or `"warning"`. |
| `location` | File the record came from (with a line number for `.jsonl`, or an index for a `.json` array). |
| `record` | The record's `id`, when known. |
| `path` | A JSON path (`$.field[index].sub`) to where the problem is. |
| `message` | Human-readable description. |

The text format prints the same information as `LEVEL   location [record] at path: message`.

## Using it in CI

The project's own [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) is the canonical example — it runs `collect check-standard --strict`, `collect validate --strict examples/postcard examples/package`, and `pytest` across Python 3.10–3.13. Point the same two `collect` commands at your own profile/vocab and record directories to get the same checks in your own catalog or collection repository.
