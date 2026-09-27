"""mkdocs-gen-files hook: assemble the site's virtual pages at build time.

This script never writes to the repository. It runs inside the mkdocs
``gen-files`` plugin and produces *virtual* files inside ``docs_dir`` (see
``mkdocs.yml``): copies of the root README/ROADMAP/CONTRIBUTING and of
``spec/*.md`` (so the site mirrors the repo's actual doc structure without
duplicating content in git), plus generated reference pages for every
schema under ``schema/0.1/`` and every profile under ``profiles/*/*/``.

The schema and profile pages are built from a glob, not a hardcoded file
list, so new profiles (or schema files) that land on disk later show up on
the next build with no changes needed here or in ``mkdocs.yml``.
"""

from __future__ import annotations

import json
from pathlib import Path

import mkdocs_gen_files

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def copy_verbatim(source: Path, dest: str) -> None:
    """Copy a repo file's content into a virtual doc page at `dest`."""
    with mkdocs_gen_files.open(dest, "w") as f:
        f.write(source.read_text(encoding="utf-8"))
    mkdocs_gen_files.set_edit_path(dest, source.relative_to(REPO_ROOT))


def render_json_page(dest: str, title: str, description: str | None, data: dict, source: Path) -> None:
    """Write a reference page: a heading/intro, then the formatted JSON."""
    lines = [f"# {title}", ""]
    if description:
        lines += [description, ""]
    lines += [
        "```json",
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False),
        "```",
        "",
    ]
    with mkdocs_gen_files.open(dest, "w") as f:
        f.write("\n".join(lines))
    mkdocs_gen_files.set_edit_path(dest, source.relative_to(REPO_ROOT))


# --- Root docs, copied verbatim so the site mirrors the repo's own layout ---

copy_verbatim(REPO_ROOT / "README.md", "index.md")
copy_verbatim(REPO_ROOT / "ROADMAP.md", "ROADMAP.md")
copy_verbatim(REPO_ROOT / "CONTRIBUTING.md", "CONTRIBUTING.md")

# --- spec/*.md, copied verbatim into docs/spec/ so relative links between
#     spec files (and the docs/*.md pages' "../spec/..." links) resolve
#     the same way inside the built site as they do in the repo. ---

for spec_file in sorted((REPO_ROOT / "spec").glob("*.md")):
    copy_verbatim(spec_file, f"spec/{spec_file.name}")

# --- Live schema browser: one page per core schema file. ---

schema_pages = []
for schema_file in sorted((REPO_ROOT / "schema" / "0.1").glob("*.schema.json")):
    data = json.loads(schema_file.read_text(encoding="utf-8"))
    title = data.get("title", schema_file.stem)
    dest = f"schema-browser/schema/{schema_file.stem}.md"
    render_json_page(dest, title, data.get("description"), data, schema_file)
    schema_pages.append((title, dest))

# --- Live schema browser: one page per profile, discovered by glob so new
#     profiles (e.g. a future `coin` or `stamp`) get a page automatically. ---

profile_pages = []
for profile_file in sorted(REPO_ROOT.glob("profiles/*/*/profile.json")):
    data = json.loads(profile_file.read_text(encoding="utf-8"))
    profile_id = profile_file.parent.parent.name
    version = profile_file.parent.name
    title = data.get("title", profile_id)
    dest = f"schema-browser/profiles/{profile_id}-{version}.md"
    render_json_page(dest, title, data.get("description"), data, profile_file)
    profile_pages.append((f"{title} ({version})", dest))

# --- Hub pages, so the profile list (which grows over time) is reachable
#     from the nav without mkdocs.yml needing to name each profile. ---

with mkdocs_gen_files.open("schema-browser/index.md", "w") as f:
    f.write("# Schema & profile browser\n\n")
    f.write(
        "Generated, read-only reference pages for every schema and profile "
        "definition in the repository — not an interactive validator (see "
        "the [roadmap](../ROADMAP.md) for that).\n\n"
    )
    f.write("## Core schemas\n\n")
    for title, dest in schema_pages:
        rel = Path(dest).relative_to("schema-browser")
        f.write(f"- [{title}]({rel})\n")
    f.write("\n## Profiles\n\n")
    for title, dest in profile_pages:
        rel = Path(dest).relative_to("schema-browser")
        f.write(f"- [{title}]({rel})\n")

with mkdocs_gen_files.open("schema-browser/profiles/index.md", "w") as f:
    f.write("# Profiles\n\n")
    f.write(
        "Every profile currently defined under `profiles/`, generated from "
        "each profile's `profile.json`. New profiles appear here "
        "automatically on the next build.\n\n"
    )
    for title, dest in profile_pages:
        rel = Path(dest).relative_to("schema-browser/profiles")
        f.write(f"- [{title}]({rel})\n")
