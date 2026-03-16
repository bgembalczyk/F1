from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.table_parsing import TableParsingHelper
from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.engine import EngineColumn
from scrapers.base.table.columns.types.entrant import EntrantColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.pipeline import TablePipeline
from scrapers.drivers.columns.points_or_text import PointsOrTextColumn
from scrapers.drivers.columns.round import RoundColumn
from scrapers.drivers.columns.series import SeriesColumn
from scrapers.drivers.columns.unknown_value import UnknownValueColumn
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


class DriverResultsSectionParser:
    _UNKNOWN_VALUE = "unknown"

    def __init__(
        self,
        *,
        url: str,
        options: ScraperOptions,
    ) -> None:
        self._url = url
        self._options = options
        self._table_parser = ArticleTablesParser(
            include_heading_path=True,
            include_source_table=True,
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        records: list[dict[str, Any]] = []
        for table_data in self._table_parser.parse(section_fragment):
            parsed = self._parse_results_table_data(table_data)
            if parsed is None:
                continue
            if "heading_path" in table_data:
                parsed["heading_path"] = table_data["heading_path"]
            records.append(parsed)
        return SectionParseResult(
            section_id="driver_results",
            section_label="Driver results",
            records=records,
            metadata={"parser": self.__class__.__name__},
        )

    def _parse_results_table_data(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        headers = table_data["headers"]
        if not headers:
            return None

        table = table_data.get("_table")
        if not isinstance(table, Tag):
            return None

        header_set = set(headers)
        if {"Season", "Series", "Position", "Team", "Car"}.issubset(header_set):
            return {
                "table_type": "career_highlights",
                "headers": headers,
                "rows": self._parse_career_highlights(table),
            }

        if {"Season", "Series", "Position"}.issubset(header_set):
            return {
                "table_type": "career_summary",
                "headers": headers,
                "rows": self._parse_career_summary(table),
            }

        if "Year" in header_set:
            return {
                "table_type": "complete_results",
                "headers": headers,
                "rows": self._parse_complete_results(table, headers),
            }

        return None

    def _parse_career_highlights(self, table: Tag) -> list[dict[str, Any]]:
        schema = TableSchemaDSL(
            columns=[
                column("Season", "season", self._unknown(IntColumn())),
                column("Series", "series", self._unknown(UrlColumn())),
                column("Position", "position", self._unknown(PositionColumn())),
                column("Team", "team", self._unknown(EntrantColumn())),
                column("Car", "car", self._unknown(UrlColumn())),
            ],
        )
        return self._parse_table(table, self._build_pipeline(schema=schema))

    def _parse_career_summary(self, table: Tag) -> list[dict[str, Any]]:
        schema = TableSchemaDSL(
            columns=[
                column("Season", "season", self._unknown(IntColumn())),
                column("Series", "series", self._unknown(SeriesColumn())),
                column("Position", "position", self._unknown(TextColumn())),
                column("Team", "team", self._unknown(EntrantColumn())),
                column("Races", "races", self._unknown(IntColumn())),
                column("Wins", "wins", self._unknown(IntColumn())),
                column("Poles", "poles", self._unknown(IntColumn())),
                column("F/Laps", "fastest_laps", self._unknown(IntColumn())),
                column("F/Lap", "fastest_laps", self._unknown(IntColumn())),
                column("Podiums", "podiums", self._unknown(IntColumn())),
                column("Points", "points", self._unknown(PointsOrTextColumn())),
            ],
        )
        return self._parse_table(table, self._build_pipeline(schema=schema))

    def _parse_complete_results(self, table: Tag, headers: list[str]) -> list[dict[str, Any]]:
        column_map = {
            "Year": "year", "Team": "team", "Co-Drivers": "co_drivers", "Co-drivers": "co_drivers",
            "Car": "car", "Class": "class", "Laps": "laps", "Pos.": "pos", "Pos": "pos",
            "Class Pos.": "class_pos", "Class Pos": "class_pos", "Entrant": "entrant", "Chassis": "chassis",
            "Engine": "engine", "WDC": "wdc", "Points": "points", "Rank": "rank", "DC": "dc",
            "Qualifying": "qualifying", "Quali Race": "quali_race", "Main race": "main_race", "Tyres": "tyres",
            "No.": "no", "No": "no", "Start": "start", "Finish": "finish", "Stages won": "stages_won",
            "Pts": "points", "Pts.": "points", "Ref": "ref", "Make": "make", "Manufacturer": "manufacturer",
            "NGNC": "ngnc", "QH": "qh", "F": "f",
        }
        columns: dict[str, Any] = {
            "year": self._unknown(AutoColumn()), "team": self._unknown(EntrantColumn()),
            "co_drivers": self._unknown(DriverListColumn()), "car": self._unknown(AutoColumn()),
            "class": self._unknown(AutoColumn()), "laps": self._unknown(IntColumn()),
            "pos": self._unknown(PositionColumn()), "class_pos": self._unknown(PositionColumn()),
            "entrant": self._unknown(EntrantColumn()),
            "chassis": self._unknown(LinksListColumn(text_for_missing_url=True)),
            "engine": self._unknown(EngineColumn()), "wdc": self._unknown(PositionColumn()),
            "points": self._unknown(PointsOrTextColumn()), "rank": self._unknown(PositionColumn()),
            "dc": self._unknown(PositionColumn()), "qualifying": self._unknown(PositionColumn()),
            "quali_race": self._unknown(PositionColumn()), "main_race": self._unknown(PositionColumn()),
            "tyres": self._unknown(TyreColumn()), "no": self._unknown(IntColumn()), "start": self._unknown(PositionColumn()),
            "finish": self._unknown(PositionColumn()), "stages_won": self._unknown(IntColumn()),
            "make": self._unknown(ConstructorColumn()), "manufacturer": self._unknown(ConstructorColumn()),
            "ngnc": self._unknown(PositionColumn()), "qh": self._unknown(PositionColumn()), "f": self._unknown(PositionColumn()),
            "ref": SkipColumn(),
        }
        schema_columns = [column(header, key, columns[key]) for header, key in column_map.items()]
        schema_columns.extend(column(header, header, self._unknown(RoundColumn())) for header in headers if header.isdigit())
        return self._parse_table(table, self._build_pipeline(schema=TableSchemaDSL(columns=schema_columns)))

    def _parse_table(self, table: Tag, pipeline: TablePipeline) -> list[dict[str, Any]]:
        return TableParsingHelper.parse_table_with_pipeline(table, pipeline)

    def _build_pipeline(self, *, schema: TableSchemaDSL) -> TablePipeline:
        config = ScraperConfig(
            url=self._url,
            section_id=None,
            expected_headers=None,
            schema=schema,
            default_column=AutoColumn(),
            record_factory=record_from_mapping,
        )
        return TablePipeline(
            config=config,
            include_urls=self._options.include_urls,
            normalize_empty_values=self._options.normalize_empty_values,
            debug_dir=self._options.debug_dir,
        )

    def _unknown(self, base_column: Any) -> UnknownValueColumn:
        return UnknownValueColumn(base_column, unknown_value=self._UNKNOWN_VALUE)
