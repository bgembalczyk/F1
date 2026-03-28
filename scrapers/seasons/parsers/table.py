from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.table.columns.types import IntColumn
from scrapers.points.columns.points import PointsColumn
from scrapers.seasons.columns.position import PositionColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
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

    @property
    def options(self) -> ScraperOptions:
        return self._options

    @property
    def include_urls(self) -> bool:
        return self._include_urls

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
    ) -> list[dict[str, Any]]:
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
                record_factory=RECORD_FACTORIES.mapping(),
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
    ) -> list[dict[str, Any]]:
        for section_id in section_ids:
            config = ScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=expected_headers,
                schema=schema,
                default_column=default_column,
                record_factory=RECORD_FACTORIES.mapping(),
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
                section_domain="seasons",
            )
            try:
                records: list[dict[str, Any]] = []
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

    def parse_table_data(
        self,
        table_data: dict[str, Any],
        *,
        expected_headers: list[str],
        schema: TableSchemaDSL,
        default_column: Any | None = None,
    ) -> list[dict[str, Any]]:
        headers = [str(value) for value in table_data.get("headers") or []]
        rows = table_data.get("rows") or []
        if not headers or not rows:
            return []
        normalized_headers = {header.strip().lower() for header in headers}
        if not all(
            expected_header.strip().lower() in normalized_headers
            for expected_header in expected_headers
        ):
            return []

        config = ScraperConfig(
            url=self.url,
            section_id="adapter_section",
            expected_headers=expected_headers,
            schema=schema,
            default_column=default_column,
            record_factory=RECORD_FACTORIES.mapping(),
        )
        pipeline = TablePipeline(
            config=config,
            include_urls=self._include_urls,
            normalize_empty_values=self._options.normalize_empty_values,
        )

        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(rows):
            if not isinstance(row, list):
                continue
            record = pipeline.parse_cells(
                headers,
                [str(cell) for cell in row],
                row_index=row_index,
            )
            if record:
                records.append(record)
        return records
