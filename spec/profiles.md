# Profiles — v0.1 (draft)

A profile extends the core with fields for one kind of collectible. The postcard profile lives in [`profiles/postcard/0.1.0/`](../profiles/postcard/0.1.0/).

## Using profile fields

A profile field is written as a top-level key `profileId:fieldName`:

```json
{
  "collect": "0.1",
  "id": "local:0042",
  "layer": "instance",
  "category": "postcard",
  "postcard:posted": true,
  "postcard:postmark": { "date": "1906-07-14", "place": "Brooklyn, N.Y." }
}
```

The validator checks that the field exists in the profile, that it is allowed on the record's layer, and that its value matches the field's schema. Values outside the field's vocabulary produce a warning.

## Defining a profile

A profile is a folder `profiles/<id>/<version>/` containing `profile.json` and, optionally, a `vocab/` folder. `profile.json` must validate against [`schema/0.1/profile.schema.json`](../schema/0.1/profile.schema.json):

```json
{
  "id": "postcard",
  "version": "0.1.0",
  "collect": "0.1",
  "title": "Postcards",
  "status": "draft",
  "categories": ["postcard"],
  "fields": {
    "era": {
      "description": "Production era.",
      "layers": ["catalog", "variant", "instance"],
      "schema": { "type": "string" },
      "vocabulary": "vocab/eras.json"
    }
  }
}
```

Guidelines for profile authors:

- **Reuse the core first.** Publishers, artists and players are `agents`; catalog numbers are `identifiers`; depicted places are `places`. Add a profile field only for something the core cannot express.
- **Allow descriptive fields on `instance` too**, so uncataloged objects can be described fully.
- **Mark personal fields `"private": true`.**
- **Prefer vocabularies to free text** for anything people will filter or sort by, and always include an `other` term.
- Field names are camelCase; vocabulary terms are lowercase-hyphenated.
- Profiles are versioned with semantic versioning. Removing or renaming a field, or narrowing what a field accepts, is a major change.

Run `collect check-standard` to validate every profile and vocabulary in the repository.

## Planned profiles

`sports-card` is next (set, card number, parallel, serial numbering, team, rookie flag, autograph and relic details). Proposals for others are welcome — open an issue using the "Profile proposal" template.
