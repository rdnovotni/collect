# Documentation

The [`spec/`](../spec/core.md) directory is the specification itself — terse and normative, written for implementers. This `docs/` directory is the explanatory layer around it: why the format is shaped the way it is, how to use it in practice, and where to look things up quickly.

| Doc | For |
|---|---|
| [Getting started](getting-started.md) | Writing and validating your first records, five minutes in. |
| [Architecture & design rationale](architecture.md) | Why the layer model, EDTF dates, namespaced profiles, and open vocabularies — and what alternatives were rejected. |
| [Schema reference](schema-reference.md) | Every field, on every layer, in one place. What to look up while writing records. |
| [CLI reference](cli-reference.md) | Every `collect` subcommand, flag, exit code, and output format. |
| [FAQ](faq.md) | Answers to questions that come up repeatedly. |

If something here and the spec disagree, the spec wins — [open an issue](https://github.com/rdnovotni/collect/issues) so we can fix the drift.

This directory, `spec/`, and a generated schema/profile browser also build into a static site (see [`mkdocs.yml`](../mkdocs.yml)); it will be live at <https://rdnovotni.github.io/collect/> once a maintainer enables GitHub Pages for this repository.

For where the project is going next, see [ROADMAP.md](../ROADMAP.md). For how to contribute, see [CONTRIBUTING.md](../CONTRIBUTING.md).
