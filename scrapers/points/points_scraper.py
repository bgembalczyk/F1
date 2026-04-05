from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions
from scrapers.base.transformers.points_scoring_systems_history import (
    PointsScoringSystemsHistoryTransformer,
)
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.config_factory import POINTS_SCORING_SYSTEMS_HISTORY_CONFIG
from scrapers.points.parsers import PointsScoringSystemsSectionParser
from scrapers.points.parsers import ShortenedRacesSubSubSectionParser
from scrapers.points.parsers import SprintRacesSubSubSectionParser
from scrapers.points.sprint_qualifying_points import SprintQualifyingPointsScraper
from scrapers.wiki.parsers.body_content import BodyContentParser


class PointsScraper(BasePointsScraper):
    """Aggregate scraper joining all points scoring tables from one article."""

    url = BasePointsScraper.BASE_URL
    _SUPPORTED_EXPORT_SCOPES = {"all", "history", "shortened", "sprint"}

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        export_scope: str = "all",
    ) -> None:
        super().__init__(
            options=options,
            config=POINTS_SCORING_SYSTEMS_HISTORY_CONFIG,
        )
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = (
                f"Unsupported export_scope='{export_scope}' for "
                f"{self.__class__.__name__}"
            )
            raise ValueError(msg)
        self._export_scope = export_scope
        parser = PointsScoringSystemsSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser
        self.sprint_subsection_parser: SprintRacesSubSubSectionParser = (
            parser.sprint_subsection_parser
        )
        self.shortened_subsection_parser: ShortenedRacesSubSubSectionParser = (
            parser.shortened_subsection_parser
        )

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        body_content = BodyContentParser.find_body_content(soup)
        parsed = self.body_content_parser.parse(body_content) if body_content else {}
        raw_history_records = self.section_parser.collect_rows(parsed)
        history_records = PointsScoringSystemsHistoryTransformer().transform(
            raw_history_records
        )
        shortened_records = self.shortened_subsection_parser.collect_rows(parsed)
        sprint_records = self.sprint_subsection_parser.collect_rows(parsed)
        if not sprint_records:
            sprint_records = self._extract_sprint_rows_via_legacy_table_scraper(soup)
        if self._export_scope == "history":
            return history_records
        if self._export_scope == "shortened":
            return shortened_records
        if self._export_scope == "sprint":
            return sprint_records
        base_payload = super()._parse_soup(soup)
        article = base_payload[0] if base_payload else {}
        return [
            {
                "url": self.url,
                "article": article,
                "points_scoring_systems_history": history_records,
                "shortened_race_points": shortened_records,
                "sprint_qualifying_points": sprint_records,
            },
        ]

    def _extract_sprint_rows_via_legacy_table_scraper(
        self,
        soup: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        legacy_scraper = SprintQualifyingPointsScraper()
        rows = legacy_scraper.parse_soup(soup)
        return [row for row in rows if isinstance(row, dict)]
