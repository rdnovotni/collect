# Collect conformance suite

A versioned, implementation-agnostic set of test cases for anyone building a
Collect validator — not just this repository's Python implementation. This
is a prerequisite for the v1.0 milestone's "a second independent
implementation passes the conformance suite" criterion (see
[`ROADMAP.md`](../ROADMAP.md)).

## Format

Each version of the suite lives in its own directory (`v0.1/`, matching the
spec version it targets) so the suite can evolve without breaking
implementations still targeting an older spec version. `v0.1/cases.json`
holds a `version` string and a `cases` array. Each case:

```json
{
  "id": "bad-date",
  "description": "'date' must be a valid EDTF string, not free text.",
  "input": { "collect": "0.1", "id": "t:1", "layer": "catalog", "date": "circa 1905" },
  "expect": { "valid": false, "level": "error", "messageContains": "not a valid EDTF date" }
}
```

- **`input`** — a single record (a JSON object), or an array of records
  when the case exercises cross-record checks (duplicate ids, reference
  targets). When `input` is an array, feed all of its records to the
  validator together, as one dataset, so references between them resolve.
- **`expect.valid`** — `true` if a conformant validator MUST report no
  errors for this input (warnings are still allowed — conformance is about
  schema, profile and reference-target checks, not about open vocabularies).
  `false` if it MUST report at least one error.
- **`expect.level`** — present when `valid` is `false`; the minimum
  severity level (`"error"`) the case's problem must be reported at.
- **`expect.messageContains`** — present when `valid` is `false`; a
  substring that MUST appear in at least one reported issue's message. This
  is deliberately loose (a substring, not an exact string or error code) so
  implementations aren't forced to match this repo's exact wording — only
  to detect the same class of problem.

## Running it against this repository's own validator

`tests/test_conformance_suite.py` runs every case in `v0.1/cases.json`
through `collect_tools.validate` and asserts it matches `expect`, so the
suite can't silently drift from what the reference implementation actually
does. Run it with the rest of the test suite: `pytest tests/test_conformance_suite.py`.

## Running it against a different implementation

Load `v0.1/cases.json`, and for each case: validate `input` (as one
combined dataset if it's an array), then check the result against `expect`
as described above. There's no required output format — only that your
validator's issues, however it represents them, contain a message matching
`messageContains` at the right severity for `valid: false` cases, and no
error-level issues for `valid: true` cases.
