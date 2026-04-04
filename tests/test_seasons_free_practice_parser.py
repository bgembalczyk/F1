from typing import Any

import pytest
from bs4 import BeautifulSoup

from scrapers.seasons.parsers.free_practice import SeasonFreePracticeParser


class _StubFreePracticeTableParser:
    def __init__(self, responses: list[list[dict[str, Any]]] | None = None, *, error: Exception | None = None) -> None:
        self._responses = responses or []
        self._error = error
        self.calls: list[dict[str, Any]] = []

    def parse_table(self, soup: BeautifulSoup, **kwargs: Any) -> list[dict[str, Any]]:
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        if self._responses:
            return self._responses.pop(0)
        return []


def test_parse_normalizes_rows_and_filters_source_footer_records() -> None:
    parser = SeasonFreePracticeParser(
        _StubFreePracticeTableParser(
            responses=[
                [
                    {
                        "constructor": {
                            "chassis_constructor": {"text": "Team A"},
                            "engine_constructor": {"text": "Engine A"},
                        },
                        "numbers": ["15"],
                        "drivers": [{"text": "Driver A"}, {"text": "Driver B"}],
                        "rounds": ["1-2", "3"],
                    },
                    {
                        "constructor": {
                            "chassis_constructor": {"text": "Source: F1"},
                            "engine_constructor": {"text": "Source: F1"},
                        },
                        "numbers": ["99"],
                        "drivers": [{"text": "Source: F1"}],
                        "rounds": ["1"],
                    },
                ],
            ],
        ),
    )

    result = parser.parse(BeautifulSoup("<html></html>", "html.parser"))

    assert len(result) == 1
    assert result[0]["practice_drivers"] == [
        {"driver": {"text": "Driver A"}, "no": 15, "rounds": [1, 2]},
        {"driver": {"text": "Driver B"}, "no": 15, "rounds": [3]},
    ]
    assert "drivers" not in result[0]
    assert "numbers" not in result[0]
    assert "rounds" not in result[0]


def test_parse_falls_back_to_second_table_shape_when_first_is_empty() -> None:
    table_parser = _StubFreePracticeTableParser(
        responses=[
            [],
            [
                {
                    "constructor": {
                        "chassis_constructor": {"text": "Team B"},
                        "engine_constructor": {"text": "Engine B"},
                    },
                    "drivers": [{"text": "Driver C"}],
                    "rounds": ["4"],
                },
            ],
        ],
    )
    parser = SeasonFreePracticeParser(table_parser)

    result = parser.parse(BeautifulSoup("<html></html>", "html.parser"))

    assert len(result) == 1
    assert result[0]["practice_drivers"] == [
        {"driver": {"text": "Driver C"}, "rounds": [4]},
    ]
    assert table_parser.calls[0]["expected_headers"] == [
        "Constructor",
        "No.",
        "Driver name",
        "Rounds",
    ]
    assert table_parser.calls[1]["expected_headers"] == [
        "Constructor",
        "Driver name",
        "Rounds",
    ]


def test_parse_falls_back_to_practice_drivers_column_variant() -> None:
    parser = SeasonFreePracticeParser(
        _StubFreePracticeTableParser(
            responses=[
                [],
                [],
                [
                    {
                        "constructor": {
                            "chassis_constructor": {"text": "Team C"},
                            "engine_constructor": {"text": "Engine C"},
                        },
                        "practice_drivers": [
                            {"driver": {"text": "Driver D"}, "rounds": [1, 2]},
                        ],
                    },
                ],
            ],
        ),
    )

    result = parser.parse(BeautifulSoup("<html></html>", "html.parser"))

    assert result == [
        {
            "constructor": {
                "chassis_constructor": {"text": "Team C"},
                "engine_constructor": {"text": "Engine C"},
            },
            "practice_drivers": [{"driver": {"text": "Driver D"}, "rounds": [1, 2]}],
        },
    ]


def test_parse_propagates_table_parser_errors() -> None:
    parser = SeasonFreePracticeParser(
        _StubFreePracticeTableParser(error=RuntimeError("table parse failed")),
    )

    with pytest.raises(RuntimeError, match="table parse failed"):
        parser.parse(BeautifulSoup("<html></html>", "html.parser"))
