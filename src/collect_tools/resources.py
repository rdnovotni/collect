"""Locate and load the standard's files: schemas, vocabularies and profiles.

Lookup order: the COLLECT_DATA_ROOT environment variable, data bundled in an
installed wheel (collect_tools/_data), then the repository checkout this file
lives in (for editable installs and running from source).
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from . import SPEC_VERSION

_MARKER = Path("schema") / SPEC_VERSION / "record.schema.json"


@lru_cache(maxsize=None)
def data_root() -> Path:
    candidates = []
    env = os.environ.get("COLLECT_DATA_ROOT")
    if env:
        candidates.append(Path(env))
    here = Path(__file__).resolve().parent
    candidates.append(here / "_data")
    candidates.extend(here.parents)
    for c in candidates:
        if (c / _MARKER).is_file():
            return c
    raise FileNotFoundError(
        "Could not find the Collect schema files. Set COLLECT_DATA_ROOT to the repository root."
    )


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def schema_dir() -> Path:
    return data_root() / "schema" / SPEC_VERSION


@lru_cache(maxsize=None)
def core_vocab(name: str) -> dict | None:
    p = data_root() / "vocab" / f"{name}.json"
    return load_json(p) if p.is_file() else None


@lru_cache(maxsize=None)
def condition_scale(scale: str) -> dict | None:
    p = data_root() / "vocab" / "condition-scales" / f"{scale}.json"
    return load_json(p) if p.is_file() else None


def term_ids(vocab: dict | None) -> set[str]:
    if not vocab:
        return set()
    ids = set()
    for t in vocab.get("terms", []):
        ids.add(t["id"])
        ids.update(t.get("aliases", []))
    return ids


@lru_cache(maxsize=None)
def profiles() -> dict[str, dict]:
    """Return {profile_id: profile} for the newest version of each bundled profile.

    Each profile dict gets a private '_dir' key pointing at its folder.
    """
    found: dict[str, dict] = {}
    root = data_root() / "profiles"
    if not root.is_dir():
        return found
    for pfile in sorted(root.glob("*/*/profile.json")):
        prof = load_json(pfile)
        prof["_dir"] = pfile.parent
        prev = found.get(prof["id"])
        if prev is None or _ver(prof["version"]) > _ver(prev["version"]):
            found[prof["id"]] = prof
    return found


def profile_vocab(profile: dict, rel_path: str) -> dict | None:
    p = Path(profile["_dir"]) / rel_path
    return load_json(p) if p.is_file() else None


def _ver(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))
