import json
from pathlib import Path

from collect_tools.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_packages_are_validated_as_separate_datasets(capsys):
    # The package holds copies of the loose example records; they must not collide.
    assert main(["validate", "--strict", str(ROOT / "examples/postcard"), str(ROOT / "examples/package")]) == 0


def test_invalid_input_exits_nonzero(capsys):
    assert main(["validate", str(ROOT / "tests/fixtures/invalid/bad-date.json")]) == 1


def test_csv2json_output_validates(tmp_path, capsys):
    out = tmp_path / "out.json"
    assert main(["csv2json", str(ROOT / "examples/csv/my-postcards.csv"), "-o", str(out)]) == 0
    assert main(["validate", "--strict", str(out)]) == 0


def test_check_standard_command(capsys):
    assert main(["check-standard", "--strict"]) == 0
    out = capsys.readouterr().out
    assert "0 error(s), 0 warning(s)" in out


def test_validate_json_format(capsys):
    assert main(["validate", "--format", "json", str(ROOT / "examples/postcard")]) == 0
    assert json.loads(capsys.readouterr().out) == []


def test_check_standard_json_format(capsys):
    assert main(["check-standard", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out) == []


def test_validate_sarif_format(capsys):
    assert main(["validate", "--format", "sarif", str(ROOT / "tests/fixtures/invalid/bad-date.json")]) == 1
    sarif = json.loads(capsys.readouterr().out)
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["tool"]["driver"]["name"] == "collect"
    result = sarif["runs"][0]["results"][0]
    assert result["level"] == "error"
    assert "EDTF" in result["message"]["text"]


def test_validate_missing_path_reports_error_and_exits(capsys):
    missing = ROOT / "tests/fixtures/does-not-exist.json"
    assert main(["validate", str(missing)]) == 2
    assert "could not read" in capsys.readouterr().err


def test_validate_malformed_json_reports_error_and_exits(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    assert main(["validate", str(bad)]) == 2
    assert "could not read" in capsys.readouterr().err


def test_init_scaffold_validates_cleanly(tmp_path, capsys):
    out = tmp_path / "scaffold.json"
    assert main(["init", "--layer", "work", "-o", str(out)]) == 0
    assert main(["validate", "--strict", str(out)]) == 0


def test_init_with_category_prints_profile_field_hint(capsys):
    assert main(["init", "--layer", "instance", "--category", "postcard"]) == 0
    out, err = capsys.readouterr()
    record = json.loads(out)
    assert record["category"] == "postcard"
    assert "postcard:era" in err


def test_init_variant_scaffold_validates_without_errors(tmp_path):
    out = tmp_path / "scaffold.json"
    assert main(["init", "--layer", "variant", "-o", str(out)]) == 0
    # Not --strict: the placeholder variantOf is an unresolved-reference warning, not an error.
    assert main(["validate", str(out)]) == 0
    assert main(["validate", "--strict", str(out)]) == 1
