from models.mappers.serialization import to_dict, to_dict_list
from models.value_objects.link import Link
from models.value_objects.normalized_date import NormalizedDate
from models.value_objects.season_ref import SeasonRef
from models.value_objects.time_types import DateValue


def test_value_object_base_from_dict_for_date_value():
    value = DateValue.from_dict({"iso": "2024-01-01", "year": 2024})

    assert isinstance(value, DateValue)
    assert value.to_dict() == {
        "iso": "2024-01-01",
        "year": 2024,
        "month": None,
        "day": None,
        "raw": None,
    }


def test_value_object_override_from_dict_for_season_ref():
    assert SeasonRef.from_dict(
        {"year": 2024, "url": "https://example.com"}
    ).to_dict() == {
        "year": 2024,
        "url": "https://example.com",
    }
    assert SeasonRef.from_dict({"url": "https://example.com"}) is None


def test_to_dict_uses_value_object_interface():
    link = Link(text="Docs", url="https://example.com")

    assert to_dict(link) == {"text": "Docs", "url": "https://example.com"}


def test_to_dict_list_uses_value_object_interface():
    dates = [NormalizedDate(text=" Test ", iso=" 2024-01-01 ")]

    assert to_dict_list(dates) == [{"text": "Test", "iso": "2024-01-01"}]
