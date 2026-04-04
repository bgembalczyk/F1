from typing import Any

import pytest
from bs4 import BeautifulSoup

from scrapers.seasons.parsers.standings import SeasonStandingsParser


class _StubStandingsTableParser:
    def __init__(
        self,
        responses: list[Any] | None = None,
        *,
        error: Exception | None = None,
    ) -> None:
        self._responses = responses or []
        self._error = error
        self.calls: list[dict[str, Any]] = []

    def parse_standings_table(
        self,
        _soup: BeautifulSoup,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        if self._responses:
            return self._responses.pop(0)
        return []


def test_parse_drivers_marks_ineligible_section_and_shares_fastest_lap() -> None:
    parser = SeasonStandingsParser(
        _StubStandingsTableParser(
            responses=[
                [
                    {
                        "driver": {"text": "Driver A"},
                        "r1": {"position": 1, "fastest_lap": True},
                    },
                    {"driver": {"text": "ineligible for Formula One points"}},
                    {
                        "driver": {"text": "Driver B"},
                        "r1": {"position": 2, "fastest_lap": True},
                    },
                ],
            ],
        ),
    )

    result = parser.parse_drivers(BeautifulSoup("<html></html>", "html.parser"))

    _expected_share_count = 2
    assert [row["driver"]["text"] for row in result] == ["Driver A", "Driver B"]
    assert result[1]["eligible_for_points"] is False
    assert result[0]["r1"]["fastest_lap_shared"] is True
    assert result[1]["r1"]["fastest_lap_shared"] is True
    assert result[0]["r1"]["fastest_lap_share_count"] == _expected_share_count


def test_parse_constructors_merges_duplicate_rows_into_one_domain_result() -> None:
    parser = SeasonStandingsParser(
        _StubStandingsTableParser(
            responses=[
                [
                    {
                        "pos": 1,
                        "points": 10,
                        "no": 11,
                        "constructor": {
                            "chassis_constructor": {"text": "Team A"},
                            "engine_constructor": {"text": "Engine A"},
                        },
                        "r1": {
                            "results": {"driver": "A"},
                            "background": "gold",
                            "pole_position": True,
                        },
                    },
                    {
                        "pos": 1,
                        "points": 10,
                        "no": 12,
                        "constructor": {
                            "chassis_constructor": {"text": "Team A"},
                            "engine_constructor": {"text": "Engine A"},
                        },
                        "r1": {"results": {"driver": "B"}, "fastest_lap": True},
                    },
                ],
            ],
        ),
    )

    result = parser.parse_constructors(BeautifulSoup("<html></html>", "html.parser"))

    assert len(result) == 1
    assert "no" not in result[0]
    assert result[0]["r1"]["results"] == [{"driver": "A"}, {"driver": "B"}]
    assert "background" not in result[0]["r1"]
    assert "pole_position" not in result[0]["r1"]
    assert "fastest_lap" not in result[0]["r1"]


def test_parse_drivers_propagates_table_parser_errors() -> None:
    parser = SeasonStandingsParser(
        _StubStandingsTableParser(error=ValueError("bad table")),
    )

    with pytest.raises(ValueError, match="bad table"):
        parser.parse_drivers(BeautifulSoup("<html></html>", "html.parser"))


def test_parse_drivers_requests_primary_and_alias_section_ids() -> None:
    _expected_season_year = 2024
    table_parser = _StubStandingsTableParser(responses=[[]])
    parser = SeasonStandingsParser(table_parser)

    parser.parse_drivers(
        BeautifulSoup("<html></html>", "html.parser"),
        season_year=_expected_season_year,
    )

    assert table_parser.calls[0]["section_ids"] == [
        "World_Drivers'_Championship_standings",
        "World_Championship_of_Drivers_standings",
    ]
    assert table_parser.calls[0]["season_year"] == _expected_season_year
