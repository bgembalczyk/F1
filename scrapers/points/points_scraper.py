from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.config_factory import POINTS_SCORING_SYSTEMS_HISTORY_CONFIG
from scrapers.points.parsers import PointsScoringSystemsSectionParser
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
            msg = f"Unsupported export_scope='{export_scope}' for {self.__class__.__name__}"
            raise ValueError(msg)
        self._export_scope = export_scope
        parser = PointsScoringSystemsSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        body_content = BodyContentParser.find_body_content(soup)
        parsed = self.body_content_parser.parse(body_content) if body_content else {}
        history_records = self._collect_table_rows(
            parsed,
            table_type="points_scoring_systems_history",
        )
        shortened_records = self._collect_table_rows(
            parsed,
            table_type="points_shortened_races",
        )
        sprint_records = self._collect_table_rows(
            parsed,
            table_type="points_sprint_races",
        )
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

    def _collect_table_rows(
        self,
        payload: dict[str, Any],
        *,
        table_type: str,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []

        def visit(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("table_type") == table_type:
                    table_rows = node.get("domain_rows", [])
                    if isinstance(table_rows, list):
                        rows.extend(
                            [row for row in table_rows if isinstance(row, dict)],
                        )
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for item in node:
                    visit(item)

        visit(payload)
        return rows

    def _extract_sprint_rows_via_legacy_table_scraper(
        self,
        soup: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        legacy_scraper = SprintQualifyingPointsScraper()
        rows = legacy_scraper._parse_soup(soup)
        return [row for row in rows if isinstance(row, dict)]
