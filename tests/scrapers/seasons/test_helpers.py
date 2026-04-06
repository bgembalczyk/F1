# ruff: noqa: E501, PLR2004
import pytest

from scrapers.seasons.helpers import season_filename


@pytest.mark.parametrize(
    ("season_info", "expected"),
    [
        ({"text": "2023"}, "2023.json"),
        ({"text": "pre-season"}, "pre_season.json"),
        ({"text": "Test Season 2009!"}, "test_season_2009.json"),
        ({"text": None}, "unknown.json"),
        ({}, "unknown.json"),
        ({"text": "  2021  "}, "2021.json"),
        ({"text": "---"}, "unknown.json"),
    ],
)
def test_season_filename(season_info: dict, expected: str) -> None:
    assert season_filename(season_info) == expected
