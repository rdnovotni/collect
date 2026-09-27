"""check_standard() only ever sees this repo's own (valid) profiles and vocabularies in
normal test runs, so its error-reporting branches need a deliberately broken data root to
exercise them."""
import json
import shutil
from pathlib import Path

import pytest

from collect_tools import resources as R
from collect_tools import validate as V

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def broken_standard_root(tmp_path, monkeypatch):
    shutil.copytree(ROOT / "schema", tmp_path / "schema")
    (tmp_path / "vocab").mkdir()
    (tmp_path / "profiles" / "bogus" / "1.0.0").mkdir(parents=True)
    (tmp_path / "profiles" / "broken" / "1.0.0").mkdir(parents=True)

    (tmp_path / "profiles" / "bogus" / "1.0.0" / "profile.json").write_text(json.dumps({
        "id": "bogus",
        "version": "1.0.0",
        "collect": "0.1",
        "title": "Bogus test profile",
        "fields": {
            "badField": {
                "description": "a field whose schema isn't valid JSON Schema",
                "layers": ["catalog"],
                "schema": {"type": "not-a-real-type"},
            },
            "missingVocab": {
                "description": "a field pointing at a vocabulary file that doesn't exist",
                "layers": ["catalog"],
                "schema": {"type": "string"},
                "vocabulary": "vocab/does-not-exist.json",
            },
        },
    }))

    (tmp_path / "profiles" / "broken" / "1.0.0" / "profile.json").write_text(json.dumps({
        "id": "broken",
        "version": "1.0.0",
        "collect": "0.1",
        "fields": {},
        # missing required 'title'
    }))

    (tmp_path / "vocab" / "no-title.json").write_text(json.dumps({
        "id": "no-title",
        "terms": [{"id": "a", "label": "A"}],
        # missing required 'title'
    }))

    (tmp_path / "vocab" / "dupes.json").write_text(json.dumps({
        "id": "dupes",
        "title": "Dupes",
        "terms": [{"id": "a", "label": "A"}, {"id": "a", "label": "A again"}],
    }))

    monkeypatch.setenv("COLLECT_DATA_ROOT", str(tmp_path))
    _clear_caches()
    yield tmp_path
    _clear_caches()


def _clear_caches():
    for fn in (R.data_root, R.profiles, R.core_vocab, R.condition_scale):
        fn.cache_clear()
    for fn in (V._registry, V._validator, V._cached_field_validator, V._allowed_keys):
        fn.cache_clear()


def test_check_standard_flags_an_invalid_field_schema(broken_standard_root):
    issues = V.check_standard()
    assert any(i.path == "$.fields.badField.schema" for i in issues)


def test_check_standard_flags_a_missing_vocabulary_file(broken_standard_root):
    issues = V.check_standard()
    assert any("missing file vocab/does-not-exist.json" in i.message for i in issues)


def test_check_standard_flags_a_profile_that_fails_its_meta_schema(broken_standard_root):
    issues = V.check_standard()
    assert any("broken" in str(i.location) and "required property" in i.message for i in issues)


def test_check_standard_flags_a_vocab_that_fails_its_meta_schema(broken_standard_root):
    issues = V.check_standard()
    assert any("no-title" in str(i.location) and "required property" in i.message for i in issues)


def test_check_standard_flags_duplicate_term_ids(broken_standard_root):
    issues = V.check_standard()
    assert any("duplicate term ids" in i.message for i in issues)
