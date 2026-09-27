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
