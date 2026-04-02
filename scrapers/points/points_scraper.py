from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.parsers import PointsScoringSystemsSectionParser
from scrapers.points.points_scoring_systems_history import (
    PointsScoringSystemsHistoryScraper,
)
from scrapers.points.shortened_race_points import ShortenedRacePointsScraper
from scrapers.points.sprint_qualifying_points import SprintQualifyingPointsScraper


class PointsScraper(BasePointsScraper):
    """Aggregate scraper joining all points scoring tables from one article."""

    CONFIG = PointsScoringSystemsHistoryScraper.CONFIG
    _SUPPORTED_EXPORT_SCOPES = {"all", "history", "shortened", "sprint"}

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        export_scope: str = "all",
    ) -> None:
        super().__init__(
            options=options,
            config=PointsScoringSystemsHistoryScraper.CONFIG,
        )
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = f"Unsupported export_scope='{export_scope}' for {self.__class__.__name__}"
            raise ValueError(msg)
        self._export_scope = export_scope
        parser = PointsScoringSystemsSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

        self._history_scraper = PointsScoringSystemsHistoryScraper(options=options)
        self._shortened_scraper = ShortenedRacePointsScraper(options=options)
        self._sprint_scraper = SprintQualifyingPointsScraper(options=options)

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if self._export_scope == "history":
            return self._history_scraper.parse(soup)
        if self._export_scope == "shortened":
            return self._shortened_scraper.parse(soup)
        if self._export_scope == "sprint":
            return self._sprint_scraper.parse(soup)
        base_payload = super()._parse_soup(soup)
        article = base_payload[0] if base_payload else {}
        return [
            {
                "url": self.url,
                "article": article,
                "points_scoring_systems_history": self._history_scraper.parse(soup),
                "shortened_race_points": self._shortened_scraper.parse(soup),
                "sprint_qualifying_points": self._sprint_scraper.parse(soup),
            },
        ]


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
