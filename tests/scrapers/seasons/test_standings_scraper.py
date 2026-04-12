from __future__ import annotations

from scrapers.columns.types.position import PositionColumn
from scrapers.standings_scraper_seasons import F1StandingsTableParser


def test_standings_scraper_replaces_tied_marker_with_previous_position() -> None:
    parser = F1StandingsTableParser()
    rows = parser.normalize_rows(
        [
            {"pos": 1, "driver": "A"},
            {"pos": PositionColumn.TIED, "driver": "B"},
            {"pos": 3, "driver": "C"},
        ],
    )

    assert rows[1]["pos"] == 1
    assert rows[2]["pos"] == 3  # noqa: PLR2004


def test_standings_scraper_keeps_none_when_tie_has_no_previous_position() -> None:
    parser = F1StandingsTableParser()
    rows = parser.normalize_rows(
        [
            {"pos": PositionColumn.TIED, "driver": "A"},
            {"pos": 2, "driver": "B"},
        ],
    )

    assert rows[0]["pos"] is None
    assert rows[1]["pos"] == 2  # noqa: PLR2004
