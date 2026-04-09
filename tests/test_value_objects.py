import pytest

from models.mappers.serialization import to_dict
from models.mappers.serialization import to_dict_list
from models.value_objects.common_terms import EntityName
from models.value_objects.common_terms import SeasonYear
from models.value_objects.common_terms import SectionId
from models.value_objects.common_terms import WikiUrl
from models.value_objects.drivers_championships import DriversChampionships
from models.value_objects.link import Link
from models.value_objects.normalized_date import NormalizedDate
from models.value_objects.rounds import Rounds
from models.value_objects.season_ref import SeasonRef
from models.value_objects.date import DateValue

SUPPORTED_SEASON_YEAR = 2026
EXPECTED_SEASONS_COUNT = 2
EXPECTED_ROUNDS_LENGTH = 3


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
    assert list(Rounds((4, 2, 4, 3)).values) == [2, 3, 4]


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
    assert SeasonYear(str(SUPPORTED_SEASON_YEAR)) == SUPPORTED_SEASON_YEAR
    assert SectionId("  Career Results ") == "career_results"
    assert EntityName("  Max   Verstappen ") == "Max Verstappen"


def test_season_year_rejects_out_of_range_values() -> None:
    with pytest.raises(ValueError, match="SeasonYear out of supported range"):
        SeasonYear(1500)


# DriversChampionships - _normalize_count errors
def test_drivers_championships_count_rejects_non_numeric() -> None:
    with pytest.raises(ValueError, match="Pole count musi być liczbą całkowitą"):
        DriversChampionships(count="abc")  # type: ignore[arg-type]


def test_drivers_championships_count_rejects_negative() -> None:
    with pytest.raises(ValueError, match="nie może być ujemne"):
        DriversChampionships(count=-1)


# DriversChampionships - _normalize_seasons duplicate year
def test_drivers_championships_rejects_duplicate_season_year() -> None:
    with pytest.raises(ValueError, match="więcej niż raz"):
        DriversChampionships(
            count=2,
            seasons=[SeasonRef(year=2005), SeasonRef(year=2005)],
        )


# DriversChampionships - from_value paths
def test_drivers_championships_from_value_returns_same_instance() -> None:
    dc = DriversChampionships(count=0)
    assert DriversChampionships.from_value(dc) is dc


def test_drivers_championships_from_value_returns_empty_for_none() -> None:
    result = DriversChampionships.from_value(None)
    assert result.count == 0
    assert result.seasons == []


def test_drivers_championships_from_value_raises_for_unsupported_type() -> None:
    with pytest.raises(TypeError, match="Nieobsługiwany typ"):
        DriversChampionships.from_value(42)  # type: ignore[arg-type]


def test_drivers_championships_from_value_parses_mapping() -> None:
    result = DriversChampionships.from_value(
        {"count": 2, "seasons": [{"year": 2005}, {"year": 2006}]},
    )
    assert result.count == EXPECTED_SEASONS_COUNT
    assert len(result.seasons) == EXPECTED_SEASONS_COUNT


# DriversChampionships - to_dict
def test_drivers_championships_to_dict_empty() -> None:
    result = DriversChampionships(count=0).to_dict()
    assert result == {"count": 0, "seasons": []}


# NormalizedDate - from_value paths
def test_normalized_date_from_value_returns_none_for_none() -> None:
    assert NormalizedDate.from_value(None) is None


def test_normalized_date_from_value_returns_same_instance() -> None:
    nd = NormalizedDate(text="test")
    assert NormalizedDate.from_value(nd) is nd


def test_normalized_date_from_value_from_mapping() -> None:
    result = NormalizedDate.from_value({"text": "Monaco", "iso": "2024-05-26"})
    assert result.text == "Monaco"
    assert result.iso == "2024-05-26"


def test_normalized_date_from_value_from_string() -> None:
    result = NormalizedDate.from_value("2024-05-26")
    assert result.text == "2024-05-26"
    assert result.iso is None


def test_normalized_date_from_value_from_other_type() -> None:
    result = NormalizedDate.from_value(2024)
    assert result.text == "2024"
    assert result.iso is None


# Rounds - various paths
def test_rounds_rejects_non_integer_value() -> None:
    with pytest.raises(ValueError, match="liczbami całkowitymi"):
        Rounds(("abc",))  # type: ignore[arg-type]


def test_rounds_rejects_zero_value() -> None:
    with pytest.raises(ValueError, match="dodatnie"):
        Rounds((0,))


def test_rounds_rejects_negative_value() -> None:
    with pytest.raises(ValueError, match="dodatnie"):
        Rounds((-1,))


def test_rounds_bool_true_when_non_empty() -> None:
    assert bool(Rounds((1, 2))) is True


def test_rounds_bool_false_when_empty() -> None:
    assert bool(Rounds(())) is False


def test_rounds_iter() -> None:
    assert list(Rounds((3, 1, 2))) == [1, 2, 3]


def test_rounds_len() -> None:
    assert len(Rounds((1, 2, 3))) == EXPECTED_ROUNDS_LENGTH


def test_rounds_getitem() -> None:
    r = Rounds((3, 1, 2))
    assert r[0] == 1


def test_rounds_eq_with_list() -> None:
    assert Rounds((1, 2, 3)) == [1, 2, 3]


def test_rounds_eq_with_tuple() -> None:
    assert Rounds((1, 2, 3)) == (1, 2, 3)


def test_rounds_eq_with_other_rounds() -> None:
    assert Rounds((1, 2)) == Rounds((2, 1))


def test_rounds_eq_returns_not_implemented_for_unknown_type() -> None:
    result = Rounds((1,)).__eq__("not a rounds")
    assert result is NotImplemented


def test_rounds_hash_is_consistent() -> None:
    r = Rounds((1, 2, 3))
    assert hash(r) == hash(r)
