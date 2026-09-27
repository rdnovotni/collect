from pathlib import Path

import pytest

from collect_tools.csvmap import CsvError, csv_to_records, records_to_csv
from collect_tools.validate import LoadedRecord, load_records, validate_records

ROOT = Path(__file__).resolve().parents[1]


def test_example_csv_converts_to_valid_records():
    records = csv_to_records((ROOT / "examples/csv/my-postcards.csv").read_text())
    assert len(records) == 3
    issues = validate_records([LoadedRecord(r, "csv") for r in records])
    assert issues == [], "\n".join(map(str, issues))
    first = records[0]
    assert first["postcard:posted"] is True
    assert first["postcard:postmark"] == {"date": "1911-03-02", "place": "Springfield"}
    assert first["acquired"]["price"] == {"amount": 3, "currency": "USD"}
    assert first["tags"] == ["main street", "downtown"]


def test_round_trip_preserves_spreadsheet_fields():
    records = [r.data for r in load_records(ROOT / "examples/postcard")]
    text, dropped = records_to_csv(records)
    back = csv_to_records(text)
    by_id = {r["id"]: r for r in back}
    inst = by_id["local:0042"]
    assert inst["condition"] == [{"scale": "postcard-basic", "value": "VG"}]
    assert inst["postcard:postmark"]["place"] == "Brooklyn, N.Y."
    assert by_id["example:catalog/pc7421"]["postcard:era"] == "undivided-back"
    assert any("relationships" in d for d in dropped)


def test_unknown_column_is_rejected():
    with pytest.raises(CsvError, match="unknown column"):
        csv_to_records("id,layer,colour\nt:1,work,blue\n")


def test_price_requires_currency():
    with pytest.raises(CsvError, match="together"):
        csv_to_records("id,layer,acquired.price\nt:1,instance,3.00\n")


def test_bad_boolean_is_rejected():
    with pytest.raises(CsvError, match="true/false"):
        csv_to_records("id,layer,postcard:posted\nt:1,instance,maybe\n")
