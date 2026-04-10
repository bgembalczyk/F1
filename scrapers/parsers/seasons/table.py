from typing import Any

from bs4 import BeautifulSoup

from models.records.factories.mapping import MappingRecordFactory
from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.points import PointsColumn
from scrapers.columns.types.position import PositionColumn
from scrapers.columns.types.race_result import RaceResultColumn
from scrapers.config_table import TableScraperConfig
from scrapers.options import ScraperOptions
from scrapers.parser_table import HtmlTableParser
from scrapers.pipeline_table import TablePipeline
from scrapers.standings_scraper_seasons import F1StandingsScraper
from scrapers.table_schema_dsl import TableSchemaDSL


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
        star_mark_note: str | None = None,
        include_car_no_column: bool = True,
    ) -> list[dict[str, Any]]:
        schema_columns = [
            ColumnSpec("Pos.", "pos", PositionColumn()),
            ColumnSpec("Pos", "pos", PositionColumn()),
            ColumnSpec(subject_header, subject_key, subject_column),
            ColumnSpec("Points", "points", PointsColumn()),
            ColumnSpec("Pts.", "points", PointsColumn()),
            ColumnSpec("Pts", "points", PointsColumn()),
            ColumnSpec("No.", "no", IntColumn()),
            ColumnSpec("No", "no", IntColumn()),
        ]
        if include_car_no_column:
            # Handle "Car<br>no." which becomes "Car no." after text extraction
            schema_columns.append(ColumnSpec("Car no.", "no", IntColumn()))
        for section_id in section_ids:
            config = TableScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=[subject_header],
                schema=TableSchemaDSL(columns=schema_columns),
                default_column=RaceResultColumn(
                    season_year=season_year,
                    star_mark_note=star_mark_note,
                ),
                record_factory=MappingRecordFactory(),
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
            config = TableScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=expected_headers,
                schema=schema,
                default_column=default_column,
                record_factory=MappingRecordFactory(),
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

        config = TableScraperConfig(
            url=self.url,
            section_id="adapter_section",
            expected_headers=expected_headers,
            schema=schema,
            default_column=default_column,
            record_factory=MappingRecordFactory(),
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


__all__ = ["SeasonTableParser"]
