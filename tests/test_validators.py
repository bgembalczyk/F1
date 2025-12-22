import pytest

from models.validation.validators import validate_link, validate_seasons, validate_status
from models.value_objects import SeasonRef


def test_validate_link_accepts_link_dict():
    link = validate_link(
        {"text": "Site", "url": "https://example.com"}, field_name="link"
    )

    assert link == {"text": "Site", "url": "https://example.com"}


def test_validate_link_accepts_none_payload():
    link = validate_link(None, field_name="link")

    assert link == {"text": "", "url": None}


def test_validate_link_rejects_invalid_url():
    with pytest.raises(ValueError, match="nieprawidłowy URL"):
        validate_link({"text": "Bad", "url": "notaurl"}, field_name="link")


def test_validate_seasons_filters_empty_and_coerces():
    seasons = validate_seasons(
        [
            {"year": 2020, "url": "https://example.com"},
            {"year": None},
            SeasonRef(year=2021),
        ]
    )

    assert seasons == [
        {"year": 2020, "url": "https://example.com"},
        {"year": 2021},
    ]


def test_validate_status_normalizes_case():
    assert validate_status(" Current ", ["current", "former"], "status") == "current"


def test_validate_status_rejects_unknown_value():
    with pytest.raises(ValueError, match="musi mieć jedną z wartości"):
        validate_status("unknown", ["current", "former"], "status")
