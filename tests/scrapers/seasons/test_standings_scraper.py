from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.seasons.standings_scraper import F1StandingsScraper


def test_standings_scraper_replaces_tied_marker_with_previous_position() -> None:
    scraper = F1StandingsScraper(
        options=ScraperOptions(),
        config=build_scraper_config(url="https://example.test", columns=[]),
    )
    scraper._extractor.extract = lambda _element: [  # noqa: SLF001
        {"pos": 1, "driver": "A"},
        {"pos": PositionColumn.TIED, "driver": "B"},
        {"pos": 3, "driver": "C"},
    ]

    rows = scraper.parse(BeautifulSoup("<table></table>", "html.parser").find("table"))

    assert rows[1]["pos"] == 1
    assert rows[2]["pos"] == 3  # noqa: PLR2004


def test_standings_scraper_keeps_none_when_tie_has_no_previous_position() -> None:
    scraper = F1StandingsScraper(
        options=ScraperOptions(),
        config=build_scraper_config(url="https://example.test", columns=[]),
    )
    scraper._extractor.extract = lambda _element: [  # noqa: SLF001
        {"pos": PositionColumn.TIED, "driver": "A"},
        {"pos": 2, "driver": "B"},
    ]

    rows = scraper.parse(BeautifulSoup("<table></table>", "html.parser").find("table"))

    assert rows[0]["pos"] is None
    assert rows[1]["pos"] == 2  # noqa: PLR2004
