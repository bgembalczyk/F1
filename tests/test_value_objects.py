import pytest

from models.mappers.serialization import to_dict
from models.mappers.serialization import to_dict_list
from models.value_objects import EntityName
from models.value_objects import SeasonYear
from models.value_objects import SectionId
from models.value_objects import WikiUrl
from models.value_objects.drivers_championships import DriversChampionships
from models.value_objects.link import Link
from models.value_objects.normalized_date import NormalizedDate
from models.value_objects.rounds import Rounds
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
        {"year": 2024, "url": "https://example.com"},
    ).to_dict() == {
        "year": 2024,
        "url": "https://example.com",
    }
    assert SeasonRef.from_dict({"url": "https://example.com"}) is None


def test_drivers_championships_validates_count_and_seasons():
    value = DriversChampionships(
        count=2,
        seasons=[SeasonRef(year=2005), SeasonRef(year=2006)],
    )

    assert value.to_dict() == {
        "count": 2,
        "seasons": [
            {"year": 2005},
            {"year": 2006},
        ],
    }


def test_drivers_championships_rejects_mismatched_count():
    with pytest.raises(ValueError, match="Liczba tytułów"):
        DriversChampionships(count=2, seasons=[SeasonRef(year=2005)])


def test_rounds_value_object_normalizes_and_sorts():
    assert Rounds.from_values([4, 2, 4, 3]).to_list() == [2, 3, 4]


def test_to_dict_uses_value_object_interface():
    link = Link(text="Docs", url="https://example.com")

    assert to_dict(link) == {"text": "Docs", "url": "https://example.com"}


def test_to_dict_list_uses_value_object_interface():
    dates = [NormalizedDate(text=" Test ", iso=" 2024-01-01 ")]

    assert to_dict_list(dates) == [{"text": "Test", "iso": "2024-01-01"}]


def test_common_value_objects_normalize_input_values() -> None:
    assert WikiUrl(" https://en.wikipedia.org/wiki/Monza ") == (
        "https://en.wikipedia.org/wiki/Monza"
    )
    assert SeasonYear("2026") == 2026
    assert SectionId("  Career Results ") == "career_results"
    assert EntityName("  Max   Verstappen ") == "Max Verstappen"


def test_season_year_rejects_out_of_range_values() -> None:
    with pytest.raises(ValueError, match="SeasonYear out of supported range"):
        SeasonYear(1500)
