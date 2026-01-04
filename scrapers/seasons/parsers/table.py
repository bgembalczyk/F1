from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.seasons.columns.race_result import RaceResultColumn
from scrapers.seasons.standings_scraper import F1StandingsScraper


class SeasonTableParser:
    def __init__(
        self,
        *,
        options: ScraperOptions,
        include_urls: bool,
        url: str,
    ) -> None:
        self._options = options
        self._include_urls = include_urls
        self.url = url

    def update_url(self, url: str) -> None:
        self.url = url

    def parse_standings_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        subject_header: str,
        subject_key: str,
        subject_column: Any,
        season_year: int | None = None,
    ) -> List[Dict[str, Any]]:
        schema_columns = [
            column("Pos.", "pos", PositionColumn()),
            column("Pos", "pos", PositionColumn()),
            column(subject_header, subject_key, subject_column),
            column("Points", "points", PointsColumn()),
            column("Pts.", "points", PointsColumn()),
            column("Pts", "points", PointsColumn()),
            column("No.", "no", IntColumn()),
            column("No", "no", IntColumn()),
            # Handle "Car<br>no." which becomes "Car no." after text extraction
            column("Car no.", "no", IntColumn()),
        ]
        for section_id in section_ids:
            config = ScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=[subject_header],
                schema=TableSchemaDSL(columns=schema_columns),
                default_column=RaceResultColumn(season_year=season_year),
                record_factory=record_from_mapping,
            )
            scraper = F1StandingsScraper(options=self._options, config=config)
            try:
                records = scraper.parse(soup)
                if records:
                    return records
            except RuntimeError:
                continue
        return []

    def parse_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        expected_headers: list[str],
        schema: TableSchemaDSL,
        default_column: Any | None = None,
    ) -> List[Dict[str, Any]]:
        for section_id in section_ids:
            config = ScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=expected_headers,
                schema=schema,
                default_column=default_column,
                record_factory=record_from_mapping,
            )
            pipeline = TablePipeline(
                config=config,
                include_urls=self._include_urls,
                normalize_empty_values=self._options.normalize_empty_values,
            )
            parser = HtmlTableParser(
                section_id=pipeline.section_id,
                fragment=pipeline.fragment,
                expected_headers=pipeline.expected_headers,
                table_css_class=pipeline.table_css_class,
            )
            try:
                records: List[Dict[str, Any]] = []
                for row_index, row in enumerate(parser.parse(soup)):
                    record = pipeline.parse_cells(
                        row.headers,
                        row.cells,
                        row_index=row_index,
                    )
                    if record:
                        records.append(record)
                if records:
                    return records
            except RuntimeError:
                continue

        return []
