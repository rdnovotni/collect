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


def test_validate_missing_path_reports_error_and_exits(capsys):
    missing = ROOT / "tests/fixtures/does-not-exist.json"
    assert main(["validate", str(missing)]) == 2
    assert "could not read" in capsys.readouterr().err


def test_validate_malformed_json_reports_error_and_exits(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    assert main(["validate", str(bad)]) == 2
    assert "could not read" in capsys.readouterr().err
