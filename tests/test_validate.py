import json
from pathlib import Path

import pytest

from collect_tools.validate import check_standard, load_records, validate_records

ROOT = Path(__file__).resolve().parents[1]
INVALID = ROOT / "tests" / "fixtures" / "invalid"
EXPECTED = json.loads((INVALID / "EXPECTED.json").read_text())


def errors(issues):
    return [i for i in issues if i.level == "error"]


def test_standard_files_are_valid():
    assert errors(check_standard()) == []


@pytest.mark.parametrize("target", ["examples/postcard", "examples/sports-card", "examples/coin", "examples/stamp", "examples/package"])
def test_examples_are_valid_without_warnings(target):
    issues = validate_records(load_records(ROOT / target))
    assert issues == [], "\n".join(map(str, issues))


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_invalid_fixture_is_rejected(name):
    issues = errors(validate_records(load_records(INVALID / f"{name}.json")))
    assert issues, f"{name} should have failed validation"
    assert any(EXPECTED[name] in i.message for i in issues), "\n".join(map(str, issues))


def test_unknown_vocabulary_terms_are_warnings_not_errors():
    rec = {"collect": "0.1", "id": "t:1", "layer": "catalog", "category": "space-rocks",
           "agents": [{"role": "wizard", "name": "Merlin"}], "postcard:era": "steampunk"}
    issues = validate_records(load_records_from(rec))
    assert errors(issues) == []
    assert len([i for i in issues if i.level == "warning"]) == 3


def test_unresolved_reference_in_same_namespace_warns():
    rec = {"collect": "0.1", "id": "local:1", "layer": "instance", "instanceOf": "local:missing"}
    issues = validate_records(load_records_from(rec))
    assert [i.level for i in issues] == ["warning"]


def test_external_reference_is_not_flagged():
    rec = {"collect": "0.1", "id": "local:1", "layer": "instance", "instanceOf": "someone-else:catalog/1"}
    assert validate_records(load_records_from(rec)) == []


@pytest.mark.parametrize("date", ["1906", "1906-07", "1906-07-14", "190X", "19XX", "1906~", "1906?", "1906%",
                                  "1905/1915", "1907/..", "../1915", "1910/1918?", "1908-XX"])
def test_valid_edtf_dates(date):
    rec = {"collect": "0.1", "id": "t:1", "layer": "work", "date": date}
    assert validate_records(load_records_from(rec)) == []


@pytest.mark.parametrize("date", ["circa 1905", "1906-13", "1906-02-32", "06/07/1906", "1906 - 1910", ""])
def test_invalid_edtf_dates(date):
    rec = {"collect": "0.1", "id": "t:1", "layer": "work", "date": date}
    assert errors(validate_records(load_records_from(rec)))


def test_non_dict_record_is_rejected():
    issues = validate_records(load_records_from("not an object"))
    assert [i.level for i in issues] == ["error"]
    assert "must be a JSON object" in issues[0].message


def test_unknown_profile_prefix_warns_but_does_not_error():
    rec = {"collect": "0.1", "id": "t:1", "layer": "catalog", "nosuchprofile:field": "x"}
    issues = validate_records(load_records_from(rec))
    assert errors(issues) == []
    assert any("unknown profile 'nosuchprofile'" in i.message for i in issues)


def test_invalid_layer_is_schema_error_and_skips_unknown_key_check():
    # An unrecognized layer means _allowed_keys() can't look up its known fields, so the
    # unknown-key check is skipped rather than flagging every key as unexpected.
    rec = {"collect": "0.1", "id": "t:1", "layer": "not-a-real-layer", "title": "x"}
    issues = errors(validate_records(load_records_from(rec)))
    assert any(i.path == "$.layer" for i in issues)
    assert not any(i.path == "$.title" for i in issues)


def test_non_string_condition_scale_is_a_schema_error_only():
    rec = {"collect": "0.1", "id": "t:1", "layer": "instance",
           "condition": [{"scale": 123, "value": "mint"}]}
    issues = validate_records(load_records_from(rec))
    assert any(i.path == "$.condition[0].scale" for i in issues)
    assert not any("condition scale" in i.message or "is not a grade" in i.message for i in issues)


def test_unknown_condition_scale_warns():
    rec = {"collect": "0.1", "id": "t:1", "layer": "instance",
           "condition": [{"scale": "made-up-scale", "value": "mint"}]}
    issues = validate_records(load_records_from(rec))
    assert [i.level for i in issues] == ["warning"]
    assert "unknown condition scale" in issues[0].message


def test_reference_check_skips_malformed_records_without_crashing():
    recs = load_records_from("oops") + load_records_from(
        {"collect": "0.1", "id": "local:1", "layer": "instance", "instanceOf": "local:missing"}
    )
    issues = validate_records(recs)
    assert any("must be a JSON object" in i.message for i in issues)
    assert any("not found in the records checked" in i.message for i in issues)


def load_records_from(rec):
    from collect_tools.validate import LoadedRecord
    return [LoadedRecord(rec, "<test>")]
