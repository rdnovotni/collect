"""Property-based tests for the EDTF date pattern (schema/0.1/common.schema.json).

Complements the example-based cases in test_validate.py with generated
well-formed and deliberately malformed dates, to catch edge cases a fixed
example list would miss.
"""
from __future__ import annotations

from hypothesis import given, settings, strategies as st

from collect_tools.validate import LoadedRecord, validate_records

_YEAR = st.one_of(
    st.integers(0, 9999).map(lambda y: f"{y:04d}"),
    st.integers(0, 999).map(lambda y: f"{y:03d}X"),
    st.integers(0, 99).map(lambda y: f"{y:02d}XX"),
)
_MONTH = st.one_of(st.integers(1, 12).map(lambda m: f"{m:02d}"), st.just("XX"))
_DAY = st.one_of(st.integers(1, 31).map(lambda d: f"{d:02d}"), st.just("XX"))
_QUALIFIER = st.sampled_from(["", "?", "~", "%"])
_SIGN = st.sampled_from(["", "-"])


@st.composite
def _date_component(draw):
    s = draw(_SIGN) + draw(_YEAR)
    if draw(st.booleans()):
        s += "-" + draw(_MONTH)
        if draw(st.booleans()):
            s += "-" + draw(_DAY)
    return s + draw(_QUALIFIER)


@st.composite
def _valid_edtf(draw):
    if draw(st.booleans()):
        return draw(_date_component())
    lo = draw(st.one_of(_date_component(), st.just("..")))
    hi = draw(st.one_of(_date_component(), st.just("..")))
    return f"{lo}/{hi}"


def _issues_for(date):
    rec = {"collect": "0.1", "id": "t:1", "layer": "work", "date": date}
    return validate_records([LoadedRecord(rec, "<test>")])


@given(_valid_edtf())
@settings(max_examples=200)
def test_generated_valid_dates_are_accepted(date):
    issues = _issues_for(date)
    assert issues == [], f"{date!r} rejected: {issues}"


@given(_date_component(), st.sampled_from([" - ", "..", "to", " "]))
@settings(max_examples=100)
def test_wrong_separator_between_two_components_is_rejected(component, sep):
    date = f"{component}{sep}{component}"
    issues = _issues_for(date)
    assert any(i.level == "error" for i in issues), f"{date!r} should be rejected"


@given(st.integers(13, 99))
@settings(max_examples=50)
def test_out_of_range_month_is_rejected(month):
    date = f"1906-{month:02d}"
    issues = _issues_for(date)
    assert any(i.level == "error" for i in issues), f"{date!r} should be rejected"


@given(st.integers(32, 99))
@settings(max_examples=50)
def test_out_of_range_day_is_rejected(day):
    date = f"1906-07-{day:02d}"
    issues = _issues_for(date)
    assert any(i.level == "error" for i in issues), f"{date!r} should be rejected"


@given(st.integers(1, 9))
@settings(max_examples=50)
def test_unpadded_numeric_month_is_rejected(digit):
    date = f"1906-{digit}"
    issues = _issues_for(date)
    assert any(i.level == "error" for i in issues), f"{date!r} should be rejected"
