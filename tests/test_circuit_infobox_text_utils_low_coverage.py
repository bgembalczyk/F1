import pytest

from scrapers.base.errors import DomainParseError
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        ({"text": "42"}, 42),
        ({"text": ""}, None),
        (None, None),
    ],
)
def test_parse_int_happy_path_and_empty_fallbacks(
    row: dict | None,
    expected: int | None,
) -> None:
    utils = InfoboxTextUtils()

    assert utils.parse_int(row) == expected


@pytest.mark.parametrize(
    ("row", "unit", "expected"),
    [
        ({"text": "5.891 km"}, "km", 5.891),
        ({"text": "3,660 mi"}, "mi", 3660.0),
        ({"text": "5.891 km"}, "mi", None),
        ({"text": ""}, "km", None),
    ],
)
def test_parse_length_handles_valid_values_and_non_matching_units(
    row: dict | None,
    unit: str,
    expected: float | None,
) -> None:
    utils = InfoboxTextUtils()

    assert utils.parse_length(row, unit=unit) == expected


def test_parse_length_wraps_value_error_as_domain_parse_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    utils = InfoboxTextUtils()

    def _raise_value_error(_: str | None, *, unit: str) -> float:
        msg = f"broken parser for unit={unit}"
        raise ValueError(msg)

    monkeypatch.setattr(
        "scrapers.circuits.infobox.services.text_utils.parse_number_with_unit",
        _raise_value_error,
    )

    with pytest.raises(DomainParseError) as exc_info:
        utils.parse_length({"text": "oops"}, unit="km")

    assert "Nie udało się sparsować długości (km)" in str(exc_info.value)


def test_prune_nulls_drops_empty_nested_values() -> None:
    utils = InfoboxTextUtils()

    raw = {
        "name": "Main Circuit",
        "aliases": [],
        "meta": {"url": None, "tags": []},
        "country": "UK",
    }

    assert utils.prune_nulls(raw) == {"name": "Main Circuit", "country": "UK"}
