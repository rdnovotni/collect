"""Validate Collect records.

Checks, in order:
  1. JSON Schema (structure, required fields, EDTF dates, id syntax).
  2. Profile fields ('postcard:era' etc.): known field, allowed on this layer, valid value.
  3. Vocabularies: unknown roles, schemes, statuses... are warnings (vocabularies are open);
     a value missing from a *known* condition scale is an error.
  4. Cross-record references: duplicate ids, and references that point at the wrong layer.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from . import resources as R

EXT_KEY = re.compile(r"^([a-z][a-z0-9-]*):([a-z][A-Za-z0-9]*)$")

# Which layers each reference field may point at.
REF_TARGET_LAYERS = {
    "instanceOf": {"catalog", "variant"},
    "variantOf": {"catalog"},
    "work": {"work"},
}


@dataclass
class Issue:
    level: str  # "error" | "warning"
    location: str  # file (and line/index) the record came from
    record: str | None  # record id, when known
    path: str  # JSON path inside the record
    message: str

    def __str__(self) -> str:
        rid = f" [{self.record}]" if self.record else ""
        where = f" at {self.path}" if self.path else ""
        return f"{self.level.upper():7} {self.location}{rid}{where}: {self.message}"


@dataclass
class LoadedRecord:
    data: object
    location: str


# ---------------------------------------------------------------- schemas


@lru_cache(maxsize=None)
def _registry() -> Registry:
    reg = Registry()
    for p in sorted(R.schema_dir().glob("*.schema.json")):
        schema = R.load_json(p)
        reg = reg.with_resource(schema["$id"], Resource.from_contents(schema))
    return reg


@lru_cache(maxsize=None)
def _validator(schema_file: str) -> Draft202012Validator:
    schema = R.load_json(R.schema_dir() / schema_file)
    return Draft202012Validator(schema, registry=_registry())


def _field_validator(schema_json: str) -> Draft202012Validator:
    return _cached_field_validator(schema_json)


@lru_cache(maxsize=None)
def _cached_field_validator(schema_json: str) -> Draft202012Validator:
    schema = json.loads(schema_json)
    schema.setdefault("$schema", "https://json-schema.org/draft/2020-12/schema")
    return Draft202012Validator(schema, registry=_registry())


def _json_path(parts: Iterable) -> str:
    out = "$"
    for p in parts:
        out += f"[{p}]" if isinstance(p, int) else f".{p}"
    return out


# ---------------------------------------------------------------- loading


def load_records(path: Path) -> list[LoadedRecord]:
    """Load records from a .json file (object or array), a .jsonl file, or a package directory."""
    path = Path(path)
    if path.is_dir():
        manifest = path / "datapackage.json"
        if manifest.is_file():
            return _load_package(path, manifest)
        out: list[LoadedRecord] = []
        for f in sorted(path.rglob("*")):
            if f.suffix in (".json", ".jsonl") and f.is_file():
                out.extend(load_records(f))
        return out
    if path.suffix == ".jsonl":
        out = []
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if line.strip():
                    out.append(LoadedRecord(json.loads(line), f"{path}:{n}"))
        return out
    data = R.load_json(path)
    if isinstance(data, list):
        return [LoadedRecord(d, f"{path}#{i}") for i, d in enumerate(data)]
    return [LoadedRecord(data, str(path))]


def _load_package(root: Path, manifest: Path) -> list[LoadedRecord]:
    pkg = R.load_json(manifest)
    out: list[LoadedRecord] = []
    for res in pkg.get("resources", []):
        rpath = res.get("path")
        if isinstance(rpath, str) and rpath.endswith((".json", ".jsonl")):
            out.extend(load_records(root / rpath))
    return out


# ---------------------------------------------------------------- checks


def validate_records(records: list[LoadedRecord]) -> list[Issue]:
    issues: list[Issue] = []
    for rec in records:
        issues.extend(_check_record(rec))
    issues.extend(_check_references(records))
    return issues


def _check_record(rec: LoadedRecord) -> Iterator[Issue]:
    d = rec.data
    loc = rec.location
    if not isinstance(d, dict):
        yield Issue("error", loc, None, "", "record must be a JSON object")
        return
    rid = d.get("id") if isinstance(d.get("id"), str) else None

    def err(path, msg):
        return Issue("error", loc, rid, path, msg)

    def warn(path, msg):
        return Issue("warning", loc, rid, path, msg)

    layer = d.get("layer")

    # 1. JSON Schema. Root-level 'unevaluatedProperties' errors are replaced by our own
    # unknown-key check: when any subschema fails, JSON Schema discards its annotations and
    # reports *every* key as unexpected, which buries the real error.
    for e in sorted(_validator("record.schema.json").iter_errors(d), key=lambda e: list(e.path)):
        if e.validator == "unevaluatedProperties" and not e.path:
            continue
        yield err(_json_path(e.path), _friendly(e))
    allowed = _allowed_keys(layer)
    if allowed:
        for key in d:
            if key not in allowed and not EXT_KEY.match(key):
                yield err(f"$.{key}", f"'{key}' is not a {layer} field (profile fields look like 'postcard:era')")

    # 2. Profile fields
    known = R.profiles()
    for key, value in d.items():
        m = EXT_KEY.match(key)
        if not m:
            continue
        pid, field = m.groups()
        prof = known.get(pid)
        if prof is None:
            yield warn(f"$.{key}", f"unknown profile '{pid}'; field not checked")
            continue
        spec = prof["fields"].get(field)
        if spec is None:
            yield err(f"$.{key}", f"profile '{pid}' {prof['version']} has no field '{field}'")
            continue
        if layer not in spec["layers"]:
            yield err(f"$.{key}", f"'{key}' is not allowed on layer '{layer}' (allowed: {', '.join(spec['layers'])})")
        fv = _field_validator(json.dumps(spec["schema"], sort_keys=True))
        for e in fv.iter_errors(value):
            yield err(_json_path([key, *e.path]), e.message)
        vocab_path = spec.get("vocabulary")
        if vocab_path and isinstance(value, str):
            ids = R.term_ids(R.profile_vocab(prof, vocab_path))
            if ids and value not in ids:
                yield warn(f"$.{key}", f"'{value}' is not in the {pid} vocabulary ({vocab_path})")

    # 3. Core vocabularies
    def vocab_check(value, vocab_name, path):
        ids = R.term_ids(R.core_vocab(vocab_name))
        if isinstance(value, str) and ids and value not in ids:
            return warn(path, f"'{value}' is not in vocab/{vocab_name}.json")
        return None

    checks = []
    checks.append(vocab_check(d.get("category"), "categories", "$.category"))
    checks.append(vocab_check(d.get("variantType"), "variant-types", "$.variantType"))
    if layer == "instance":
        checks.append(vocab_check(d.get("status"), "instance-statuses", "$.status"))
    for i, a in enumerate(_objs(d.get("agents"))):
        checks.append(vocab_check(a.get("role"), "agent-roles", f"$.agents[{i}].role"))
    for i, p in enumerate(_objs(d.get("places"))):
        checks.append(vocab_check(p.get("role"), "place-roles", f"$.places[{i}].role"))
    for i, x in enumerate(_objs(d.get("identifiers"))):
        checks.append(vocab_check(x.get("scheme"), "identifier-schemes", f"$.identifiers[{i}].scheme"))
    for i, r in enumerate(_objs(d.get("relationships"))):
        checks.append(vocab_check(r.get("type"), "relationship-types", f"$.relationships[{i}].type"))
    for i, img in enumerate(_objs(d.get("images"))):
        rights = img.get("rights") if isinstance(img.get("rights"), dict) else {}
        checks.append(vocab_check(rights.get("status"), "rights-statuses", f"$.images[{i}].rights.status"))
        if rights.get("status") == "licensed" and not rights.get("license"):
            checks.append(err(f"$.images[{i}].rights", "status 'licensed' requires a 'license' (SPDX id)"))
    yield from (c for c in checks if c)

    for i, c in enumerate(_objs(d.get("condition"))):
        scale = c.get("scale")
        if not isinstance(scale, str):
            continue
        vocab = R.condition_scale(scale)
        if vocab is None:
            yield warn(f"$.condition[{i}].scale", f"unknown condition scale '{scale}'; value not checked")
        elif c.get("value") not in R.term_ids(vocab):
            yield err(f"$.condition[{i}].value", f"'{c.get('value')}' is not a grade on the '{scale}' scale")


_FRIENDLY_PATTERNS = {
    "A date in Extended": "is not a valid EDTF date (examples: 1906, 1906-07-14, 190X, 1906~, 1905/1915)",
    "A record identifier": "is not a valid id (expected 'prefix:path', e.g. local:0042, or a URI)",
    "A lowercase vocabulary term": "should be a lowercase-hyphenated term, e.g. 'same-image-as'",
}


def _friendly(e) -> str:
    if e.validator == "pattern" and isinstance(e.schema, dict):
        desc = e.schema.get("description", "")
        for start, msg in _FRIENDLY_PATTERNS.items():
            if desc.startswith(start):
                return f"{e.instance!r} {msg}"
    return e.message


@lru_cache(maxsize=None)
def _allowed_keys(layer) -> frozenset[str]:
    record = R.load_json(R.schema_dir() / "record.schema.json")
    if layer not in record["$defs"]:
        return frozenset()
    common = R.load_json(R.schema_dir() / "common.schema.json")
    keys = set(common["$defs"]["baseRecord"]["properties"])
    keys |= set(record["$defs"][layer].get("properties", {}))
    return frozenset(keys)


def _objs(v) -> list[dict]:
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


def _check_references(records: list[LoadedRecord]) -> Iterator[Issue]:
    by_id: dict[str, LoadedRecord] = {}
    prefixes: set[str] = set()
    for rec in records:
        d = rec.data
        if not isinstance(d, dict) or not isinstance(d.get("id"), str):
            continue
        rid = d["id"]
        if rid in by_id:
            yield Issue("error", rec.location, rid, "$.id", f"duplicate id (first seen in {by_id[rid].location})")
            continue
        by_id[rid] = rec
        prefixes.add(rid.split(":", 1)[0])

    for rec in records:
        d = rec.data
        if not isinstance(d, dict):
            continue
        rid = d.get("id") if isinstance(d.get("id"), str) else None
        refs: list[tuple[str, str, set[str] | None]] = []
        for field, layers in REF_TARGET_LAYERS.items():
            if isinstance(d.get(field), str):
                refs.append((f"$.{field}", d[field], layers))
        for i, r in enumerate(_objs(d.get("relationships"))):
            if isinstance(r.get("target"), str):
                refs.append((f"$.relationships[{i}].target", r["target"], None))
        for i, e in enumerate(_objs(d.get("entries"))):
            if isinstance(e.get("ref"), str):
                refs.append((f"$.entries[{i}].ref", e["ref"], None))

        for path, target, layers in refs:
            tgt = by_id.get(target)
            if tgt is None:
                # Only complain when the target looks like it belongs to this dataset.
                if target.split(":", 1)[0] in prefixes:
                    yield Issue("warning", rec.location, rid, path, f"reference '{target}' not found in the records checked")
                continue
            tlayer = tgt.data.get("layer")
            if layers and tlayer not in layers:
                yield Issue(
                    "error", rec.location, rid, path,
                    f"'{target}' is a {tlayer} record; expected {' or '.join(sorted(layers))}",
                )


# ---------------------------------------------------------------- standard self-check


def check_standard() -> list[Issue]:
    """Validate the standard's own files: profiles and vocabularies against their meta-schemas."""
    issues: list[Issue] = []
    root = R.data_root()
    pv = _validator("profile.schema.json")
    vv = _validator("vocabulary.schema.json")
    for p in sorted((root / "profiles").glob("*/*/profile.json")):
        prof = R.load_json(p)
        for e in pv.iter_errors(prof):
            issues.append(Issue("error", str(p), prof.get("id"), _json_path(e.path), e.message))
        for name, spec in prof.get("fields", {}).items():
            try:
                Draft202012Validator.check_schema(spec["schema"])
            except Exception as ex:  # noqa: BLE001
                issues.append(Issue("error", str(p), prof.get("id"), f"$.fields.{name}.schema", str(ex).splitlines()[0]))
            vp = spec.get("vocabulary")
            if vp and not (p.parent / vp).is_file():
                issues.append(Issue("error", str(p), prof.get("id"), f"$.fields.{name}.vocabulary", f"missing file {vp}"))
    vocab_files = list((root / "vocab").rglob("*.json")) + list((root / "profiles").glob("*/*/vocab/*.json"))
    for p in sorted(vocab_files):
        voc = R.load_json(p)
        for e in vv.iter_errors(voc):
            issues.append(Issue("error", str(p), voc.get("id"), _json_path(e.path), e.message))
        ids = [t.get("id") for t in voc.get("terms", [])]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            issues.append(Issue("error", str(p), voc.get("id"), "$.terms", f"duplicate term ids: {sorted(dupes)}"))
    return issues


def issues_to_json(issues: list[Issue]) -> str:
    return json.dumps([asdict(i) for i in issues], indent=2)
