import pytest
from scripts.bump_version import next_patch


def test_simple_patch_bump():
    assert next_patch("v1.0.0") == "v1.0.1"


def test_higher_numbers_bump():
    assert next_patch("v1.2.9") == "v1.2.10"


def test_accepts_tag_without_v_prefix():
    assert next_patch("2.3.4") == "v2.3.5"


def test_empty_or_none_starts_at_v1_0_0():
    assert next_patch("") == "v1.0.0"
    assert next_patch(None) == "v1.0.0"


def test_rejects_non_semver():
    with pytest.raises(ValueError):
        next_patch("v1.0")
