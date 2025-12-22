from dataclasses import dataclass

import pytest

from models.validation.validators import (
    validate_int,
    validate_float,
    validate_link,
    validate_links,
    validate_seasons,
    model_to_dict,
    normalize_link_list,
    normalize_season_list,
)
from models.value_objects import Link, SeasonRef


def test_validate_int_allows_none_and_rejects_invalid_values():
    assert validate_int(None, "value") is None

    with pytest.raises(ValueError, match="musi być liczbą"):
        validate_int("bad", "value")

    with pytest.raises(ValueError, match="nie może być ujemne"):
        validate_int(-1, "value")


def test_validate_float_coerces_and_rejects_negative_values():
    assert validate_float("3.5", "value") == 3.5

    with pytest.raises(ValueError, match="nie może być ujemne"):
        validate_float(-1.0, "value")


def test_validate_link_accepts_link_instance():
    link = Link(text="Example", url="https://example.com")

    assert validate_link(link, field_name="link") == link.to_dict()


def test_validate_links_filters_empty_entries():
    links = validate_links(
        [
            Link(),
            {"text": "Example", "url": "https://example.com"},
        ],
        field_name="links",
    )

    assert links == [{"text": "Example", "url": "https://example.com"}]


def test_validate_seasons_rejects_invalid_url():
    with pytest.raises(ValueError, match="Pole seasons zawiera nieprawidłowy URL"):
        validate_seasons([{"year": 2024, "url": "bad-url"}])


def test_model_to_dict_supports_multiple_model_shapes():
    class DumpModel:
        def model_dump(self):
            return {"source": "dump"}

    class DictModel:
        def dict(self):
            return {"source": "dict"}

    @dataclass
    class DataClassModel:
        value: int

    assert model_to_dict(DumpModel()) == {"source": "dump"}
    assert model_to_dict(DictModel()) == {"source": "dict"}
    assert model_to_dict(DataClassModel(value=1)) == {"value": 1}

    with pytest.raises(TypeError, match="Nieobsługiwany typ modelu"):
        model_to_dict(123)


def test_normalize_link_list_filters_empty_links():
    links = normalize_link_list(
        [
            {"text": "", "url": None},
            {"text": "Example", "url": None},
        ]
    )

    assert links == [Link(text="Example", url=None)]


def test_normalize_season_list_filters_none_entries():
    seasons = normalize_season_list(
        [
            {"year": 2020},
            {"url": "https://example.com"},
            SeasonRef(year=2021),
        ]
    )

    assert seasons == [SeasonRef(year=2020), SeasonRef(year=2021)]
