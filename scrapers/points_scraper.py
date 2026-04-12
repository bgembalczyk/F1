from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base_points_scraper import BasePointsScraper
from scrapers.config_factory_points import POINTS_SCORING_SYSTEMS_HISTORY_CONFIG
from scrapers.errors import ScraperParseError
from scrapers.options import ScraperOptions
from scrapers.parsers.wiki.body_content import BodyContentAssembler
from scrapers.parsers_points import PointsScoringSystemsSectionParser
from scrapers.parsers_points import ShortenedRacesSubSubSectionParser
from scrapers.parsers_points import SprintRacesSubSubSectionParser
from scrapers.transformers.record.points_scoring_systems_history import (
    PointsScoringSystemsHistoryTransformer,
)

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


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
        body_content = BodyContentAssembler.find_body_content(soup)
        parsed = self.body_content_parser.parse(body_content) if body_content else {}
        raw_history_records = self.section_parser.collect_rows(parsed)
        history_records = PointsScoringSystemsHistoryTransformer().transform(
            raw_history_records,
        )
        shortened_records = self.shortened_subsection_parser.collect_rows(parsed)
        sprint_records = self.sprint_subsection_parser.collect_rows(parsed)
        if not sprint_records:
            self._raise_missing_sprint_rows()
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

    def _raise_missing_sprint_rows(self) -> None:
        msg = (
            "Missing sprint rows in canonical points parser output "
            "(section_id='Sprint_races')."
        )
        raise ScraperParseError(msg)
