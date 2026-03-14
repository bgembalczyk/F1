from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.html_utils import find_section_tables
from scrapers.base.helpers.table_parsing import TableParsingHelper
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.seasons.columns.calendar_circuit import CalendarCircuitColumn
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.parsers.table import SeasonTableParser

EXPECTED_HEADERS = ["Grand Prix", "Circuit"]
CANCELLED_ROUNDS_TABLE_INDEX = 1
MIN_TABLES_WITH_CANCELLED = 2


class CancelledRoundsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        season_year: int | None,
        calendar_data: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        schema_columns = [
            column("Grand Prix", "grand_prix", UrlColumn()),
            column("Circuit", "circuit", CalendarCircuitColumn()),
            column(
                "Scheduled date",
                "scheduled_date",
                SeasonDateColumn(year=season_year),
            ),
            column(
                "Original date",
                "scheduled_date",
                SeasonDateColumn(year=season_year),
            ),
            column("Date", "scheduled_date", SeasonDateColumn(year=season_year)),
        ]
        schema = TableSchemaDSL(columns=schema_columns)

        section_ids = ["Cancelled_Grands_Prix", "Provisional_calendar", "Calendar"]
        for section_id in section_ids:
            records = self._parse_section(
                soup,
                section_id=section_id,
                expected_headers=EXPECTED_HEADERS,
                schema=schema,
                calendar_data=calendar_data,
            )
            if records is not None:
                return records

        return []

    def _parse_section(
        self,
        soup: BeautifulSoup,
        section_id: str,
        expected_headers: list[str],
        schema: TableSchemaDSL,
        calendar_data: list[dict[str, Any]] | None,
    ) -> list[dict[str, Any]] | None:
        matching_tables = self._find_all_matching_tables(
            soup,
            section_id,
            expected_headers,
        )

        if not matching_tables:
            return None

        table_to_parse = self._select_table(matching_tables)
        records = self._parse_table_with_schema(table_to_parse, schema, section_id)

        if calendar_data is not None:
            if self._is_same_as_calendar(records, calendar_data):
                return []

        return records

    @staticmethod
    def _select_table(matching_tables: list[Tag]) -> Tag:
        if len(matching_tables) >= MIN_TABLES_WITH_CANCELLED:
            return matching_tables[CANCELLED_ROUNDS_TABLE_INDEX]
        return matching_tables[0]

    def _find_all_matching_tables(
        self,
        soup: BeautifulSoup,
        section_id: str,
        expected_headers: list[str],
    ) -> list[Tag]:
        try:
            candidate_tables = find_section_tables(soup, section_id)
        except RuntimeError:
            return []

        parser = HtmlTableParser(section_id=None, expected_headers=expected_headers)
        return [
            table
            for table in candidate_tables
            if self._table_has_expected_headers(parser, table)
        ]

    @staticmethod
    def _table_has_expected_headers(parser: HtmlTableParser, table: Tag) -> bool:
        try:
            headers, _, _ = parser._extract_headers(table)
        except RuntimeError:
            return False
        return parser._headers_match(headers)

    def _parse_table_with_schema(
        self,
        table: Tag,
        schema: TableSchemaDSL,
        section_id: str,
    ) -> list[dict[str, Any]]:
        config = ScraperConfig(
            url=self._table_parser.url,
            section_id=section_id,
            expected_headers=EXPECTED_HEADERS,
            schema=schema,
            default_column=None,
            record_factory=record_from_mapping,
        )
        pipeline = TablePipeline(
            config=config,
            include_urls=self._table_parser.include_urls,
            normalize_empty_values=self._table_parser.options.normalize_empty_values,
        )
        return TableParsingHelper.parse_table_with_pipeline(table, pipeline)

    def _is_same_as_calendar(
        self,
        cancelled_data: list[dict[str, Any]],
        calendar_data: list[dict[str, Any]],
    ) -> bool:
        if len(cancelled_data) != len(calendar_data):
            return False

        cancelled_fields = self._extract_key_fields(cancelled_data)
        calendar_fields = self._extract_key_fields(calendar_data)
        return cancelled_fields == calendar_fields

    @staticmethod
    def _extract_key_fields(data: list[dict[str, Any]]) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        for item in data:
            gp = item.get("grand_prix", {})
            circuit = item.get("circuit", {})

            gp_text = gp.get("text", "") if isinstance(gp, dict) else str(gp)
            circuit_text = CancelledRoundsParser._extract_circuit_text(circuit)
            result.append((gp_text, circuit_text))

        return result

    @staticmethod
    def _extract_circuit_text(circuit: Any) -> str:
        if not isinstance(circuit, dict):
            return str(circuit)

        circuit_inner = circuit.get("circuit", circuit)
        if isinstance(circuit_inner, dict):
            return str(circuit_inner.get("text", ""))
        return str(circuit_inner)
