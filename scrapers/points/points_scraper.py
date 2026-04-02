from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.parsers import PointsScoringSystemsSectionParser
from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.dsl.column import column
from scrapers.points.columns.first_place import FirstPlaceColumn
from scrapers.points.constants import HISTORICAL_POSITIONS
from scrapers.points.constants import POINTS_CONSTRUCTORS_CHAMPIONSHIP_HEADER
from scrapers.points.constants import POINTS_DRIVERS_CHAMPIONSHIP_HEADER
from scrapers.points.constants import POINTS_FASTEST_LAP_HEADER
from scrapers.points.constants import POINTS_NOTES_HEADER
from scrapers.points.constants import POINTS_SCORING_HISTORY_EXPECTED_HEADERS
from scrapers.points.constants import POINTS_SEASONS_HEADER
from scrapers.wiki.parsers.body_content import BodyContentParser


class PointsScraper(BasePointsScraper):
    """Aggregate scraper joining all points scoring tables from one article."""

    schema_columns = [column(POINTS_SEASONS_HEADER, "seasons", SeasonsColumn())]
    for index, position in enumerate(HISTORICAL_POSITIONS):
        column_instance = FirstPlaceColumn() if index == 0 else IntColumn()
        schema_columns.append(column(position, position.lower(), column_instance))
    schema_columns.extend(
        [
            column(POINTS_FASTEST_LAP_HEADER, "fastest_lap", IntColumn()),
            column(
                POINTS_DRIVERS_CHAMPIONSHIP_HEADER,
                "drivers_championship",
                AutoColumn(),
            ),
            column(
                POINTS_CONSTRUCTORS_CHAMPIONSHIP_HEADER,
                "constructors_championship",
                AutoColumn(),
            ),
            column(POINTS_NOTES_HEADER, "notes", SkipColumn()),
        ],
    )
    CONFIG = build_scraper_config(
        url=BasePointsScraper.BASE_URL,
        section_id="Points_scoring_systems",
        expected_headers=POINTS_SCORING_HISTORY_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=RECORD_FACTORIES.mapping(),
    )
    _SUPPORTED_EXPORT_SCOPES = {"all", "history", "shortened", "sprint"}

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        export_scope: str = "all",
    ) -> None:
        super().__init__(
            options=options,
            config=self.CONFIG,
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


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
