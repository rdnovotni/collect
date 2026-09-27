"""Convert between Collect records and flat CSV rows (spec/csv.md).

CSV is deliberately lossy: it covers what a collector would keep in a spreadsheet.
Relationships, sources, provenance, collection entries and some sub-fields are
dropped on export, and the converter reports what was dropped.
"""
from __future__ import annotations

import csv
import io
import re
from collections import OrderedDict

from . import SPEC_VERSION
from . import resources as R

SEP = "; "

SCALARS = [
    "id", "layer", "category", "title", "description", "date", "number", "work",
    "variantOf", "variantType", "instanceOf", "quantity", "status", "owner", "purpose",
    "storage", "notes",
]
ACQUIRED = ["date", "from", "venue", "note"]
LOSSY = ["relationships", "sources", "provenance", "entries", "meta"]
KEY_ORDER = [
    "collect", "id", "layer", "category", "title", "description", "date", "number",
    "work", "variantOf", "variantType", "instanceOf", "quantity", "status", "agents",
    "identifiers", "places", "condition", "acquired", "images", "tags", "storage", "notes",
]
EXT_COL = re.compile(r"^([a-z][a-z0-9-]*):([a-z][A-Za-z0-9]*)(?:\.([A-Za-z][A-Za-z0-9]*))?$")


class CsvError(ValueError):
    pass


# ---------------------------------------------------------------- JSON -> CSV


def records_to_csv(records: list[dict]) -> tuple[str, list[str]]:
    """Return (csv_text, notes about dropped data)."""
    rows: list[OrderedDict] = []
    dropped: list[str] = []
    for d in records:
        row: OrderedDict[str, str] = OrderedDict()
        rid = d.get("id", "?")
        for k in SCALARS:
            if k in d and not isinstance(d[k], (dict, list)):
                row[k] = str(d[k])
        if d.get("tags"):
            row["tags"] = SEP.join(d["tags"])
        _group(row, d.get("agents"), "agent", "role", "name", None)
        _group(row, d.get("identifiers"), "identifier", "scheme", "value", None)
        _group(row, d.get("places"), "place", "role", "name", "depicted")
        _group(row, d.get("condition"), "condition", "scale", "value", None)
        acq = d.get("acquired") or {}
        for k in ACQUIRED:
            if k in acq:
                row[f"acquired.{k}"] = str(acq[k])
        if "price" in acq:
            row["acquired.price"] = _num(acq["price"]["amount"])
            row["acquired.currency"] = acq["price"]["currency"]
        imgs = d.get("images") or []
        if imgs:
            _group(row, [{"side": i.get("side") or "other", "v": i.get("file") or i.get("url")} for i in imgs],
                   "image", "side", "v", None)
            statuses = {i["rights"]["status"] for i in imgs}
            licenses = {i["rights"].get("license") for i in imgs} - {None}
            if len(statuses) == 1:
                row["image.rights"] = next(iter(statuses))
            else:
                row["image.rights"] = "unknown"
                dropped.append(f"{rid}: images have mixed rights statuses; exported as 'unknown'")
            if len(licenses) == 1:
                row["image.license"] = licenses.pop()
        for k, v in d.items():
            if EXT_COL.match(k):
                if isinstance(v, dict):
                    for sk, sv in v.items():
                        row[f"{k}.{sk}"] = _cell(sv)
                elif isinstance(v, list):
                    dropped.append(f"{rid}: list-valued field '{k}' not exported")
                else:
                    row[k] = _cell(v)
        for k in LOSSY:
            if d.get(k):
                dropped.append(f"{rid}: '{k}' not representable in CSV")
        for a in d.get("agents") or []:
            if set(a) - {"role", "name"}:
                dropped.append(f"{rid}: extra agent details (id/identifiers/note) dropped")
                break
        rows.append(row)

    header: list[str] = [k for k in SCALARS if any(k in r for r in rows)]
    for r in rows:
        for k in r:
            if k not in header:
                header.append(k)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue(), dropped


def _group(row, items, prefix, key, val, default):
    for it in items or []:
        col = f"{prefix}.{it.get(key) or default}"
        row[col] = f"{row[col]}{SEP}{it[val]}" if col in row else str(it[val])


def _cell(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return _num(v) if isinstance(v, (int, float)) else str(v)


def _num(v) -> str:
    return str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)


# ---------------------------------------------------------------- CSV -> JSON


def csv_to_records(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    out = []
    for n, row in enumerate(reader, start=2):  # header is line 1
        try:
            out.append(_row_to_record(row))
        except CsvError as e:
            raise CsvError(f"line {n}: {e}") from None
    return out


def _split(v: str) -> list[str]:
    return [p.strip() for p in v.split(";") if p.strip()]


def _row_to_record(row: dict) -> dict:
    d: dict = {"collect": SPEC_VERSION}
    acquired: dict = {}
    images: list[dict] = []
    rights = {"status": (row.get("image.rights") or "").strip() or "unknown"}
    if (row.get("image.license") or "").strip():
        rights["license"] = row["image.license"].strip()

    for col, raw in row.items():
        if col is None:
            raise CsvError("row has more cells than the header")
        v = (raw or "").strip()
        if not v or col in ("image.rights", "image.license"):
            continue
        if col in SCALARS:
            d[col] = _int(v, col) if col == "quantity" else v
        elif col == "tags":
            d["tags"] = _split(v)
        elif col.startswith("agent."):
            d.setdefault("agents", []).extend({"role": col[6:], "name": x} for x in _split(v))
        elif col.startswith("identifier."):
            d.setdefault("identifiers", []).extend({"scheme": col[11:], "value": x} for x in _split(v))
        elif col.startswith("place."):
            d.setdefault("places", []).extend({"role": col[6:], "name": x} for x in _split(v))
        elif col.startswith("condition."):
            d.setdefault("condition", []).extend({"scale": col[10:], "value": x} for x in _split(v))
        elif col.startswith("image."):
            for x in _split(v):
                img = {"url": x} if x.startswith(("http://", "https://")) else {"file": x}
                img["side"] = col[6:]
                img["rights"] = dict(rights)
                images.append(img)
        elif col == "acquired.price":
            acquired["price"] = {"amount": _float(v, col)}
        elif col == "acquired.currency":
            acquired.setdefault("price", {})["currency"] = v
        elif col.startswith("acquired.") and col[9:] in ACQUIRED:
            acquired[col[9:]] = v
        elif m := EXT_COL.match(col):
            pid, field, sub = m.groups()
            val = _coerce(pid, field, sub, v, col)
            if sub:
                d.setdefault(f"{pid}:{field}", {})[sub] = val
            else:
                d[f"{pid}:{field}"] = val
        else:
            raise CsvError(f"unknown column '{col}' (see spec/csv.md)")

    if acquired:
        if "price" in acquired and set(acquired["price"]) != {"amount", "currency"}:
            raise CsvError("acquired.price and acquired.currency must be given together")
        d["acquired"] = acquired
    if images:
        d["images"] = images
    return {k: d[k] for k in sorted(d, key=lambda k: (KEY_ORDER.index(k) if k in KEY_ORDER else len(KEY_ORDER), k))}


def _coerce(pid, field, sub, v, col):
    prof = R.profiles().get(pid)
    spec = (prof or {}).get("fields", {}).get(field)
    if spec is None:
        return v  # the validator will report unknown profiles/fields
    schema = spec["schema"]
    if sub:
        schema = schema.get("properties", {}).get(sub, {})
    t = schema.get("type")
    if t == "boolean":
        if v.lower() in ("true", "yes", "y", "1"):
            return True
        if v.lower() in ("false", "no", "n", "0"):
            return False
        raise CsvError(f"column '{col}' expects true/false, got '{v}'")
    if t == "integer":
        return _int(v, col)
    if t == "number":
        return _float(v, col)
    return v


def _int(v, col):
    try:
        return int(v)
    except ValueError:
        raise CsvError(f"column '{col}' expects a whole number, got '{v}'") from None


def _float(v, col):
    try:
        f = float(v.replace(",", "").lstrip("$"))
    except ValueError:
        raise CsvError(f"column '{col}' expects a number, got '{v}'") from None
    return int(f) if f.is_integer() else f
