"""Runs the versioned, implementation-agnostic suite in conformance/ through
this repository's own validator, so the suite can't silently drift from what
the reference implementation actually does. See conformance/README.md.
"""
import json
from pathlib import Path

import pytest

from collect_tools.validate import LoadedRecord, validate_records

ROOT = Path(__file__).resolve().parents[1]
SUITE = json.loads((ROOT / "conformance" / "v0.1" / "cases.json").read_text())


def _validate(input_):
    records = input_ if isinstance(input_, list) else [input_]
    return validate_records([LoadedRecord(r, f"<conformance:{i}>") for i, r in enumerate(records)])


@pytest.mark.parametrize("case", SUITE["cases"], ids=lambda c: c["id"])
def test_conformance_case(case):
    issues = _validate(case["input"])
    errors = [i for i in issues if i.level == "error"]
    expect = case["expect"]
    if expect["valid"]:
        assert errors == [], f"{case['id']}: expected no errors, got {errors}"
    else:
        assert errors, f"{case['id']}: expected an error, got none"
        level = expect.get("level", "error")
        matching = [i for i in issues if i.level == level]
        assert matching, f"{case['id']}: expected a '{level}' issue, got {issues}"
        needle = expect.get("messageContains")
        if needle:
            assert any(needle in i.message for i in matching), (
                f"{case['id']}: no {level} issue contains {needle!r}: {matching}"
            )
