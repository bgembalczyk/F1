from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.html_utils import find_section_elements
from scrapers.base.helpers.table_parsing import TableParsingHelper
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL
from scrapers.base.table.dsl import column
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.seasons.columns.calendar_circuit import CalendarCircuitColumn
from scrapers.seasons.columns.date import SeasonDateColumn
from scrapers.seasons.parsers.table import SeasonTableParser


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

        # Try different sections in order
        section_ids = ["Cancelled_Grands_Prix", "Provisional_calendar", "Calendar"]

        for section_id in section_ids:
            records = self._parse_section(
                soup,
                section_id=section_id,
                expected_headers=["Grand Prix", "Circuit"],
                schema=schema,
                calendar_data=calendar_data,
            )
            # None means no tables found in this section, try next section
            # Empty list means tables found but no cancelled_rounds (matched calendar)
            if records is not None:  # Explicitly check for None vs empty list
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
        """
        Parse tables in a section with special logic for cancelled_rounds:
        - If 2 tables found: return the second one
        - If 1 table found and it matches calendar: return empty list
        - If 1 table found and doesn't match calendar: return it
        - If no tables found: return None (try next section)
        """
        # Find all matching tables in the section
        matching_tables = self._find_all_matching_tables(
            soup,
            section_id,
            expected_headers,
        )

        if not matching_tables:
            return None  # No tables found, try next section

        if len(matching_tables) >= 2:
            # If there are 2+ tables, cancelled_rounds is the second one
            table_to_parse = matching_tables[1]
        else:
            # Only one table found
            table_to_parse = matching_tables[0]

        # Parse the selected table
        records = self._parse_table_with_schema(table_to_parse, schema, section_id)

        # If only one table was found and calendar_data is provided, check if it's the same
        if len(matching_tables) == 1 and calendar_data is not None:
            if self._is_same_as_calendar(records, calendar_data):
                # This is the calendar table, not cancelled_rounds
                return []

        return records

    def _find_all_matching_tables(
        self,
        soup: BeautifulSoup,
        section_id: str,
        expected_headers: list[str],
    ) -> list[Tag]:
        """Find all tables in a section that match the expected headers."""
        try:
            candidate_tables = find_section_elements(
                soup,
                section_id,
                ["table"],
                class_="wikitable",
            )
        except RuntimeError:
            return []

        matching_tables = []
        for table in candidate_tables:
            try:
                # Create parser without section_id since table is already found
                parser = HtmlTableParser(
                    section_id=None,  # Table already found, no need to re-filter by section
                    expected_headers=expected_headers,
                )
                headers, _, _ = parser._extract_headers(table)
                if parser._headers_match(headers):
                    matching_tables.append(table)
            except RuntimeError:
                continue

        return matching_tables

    def _parse_table_with_schema(
        self,
        table: Tag,
        schema: TableSchemaDSL,
        section_id: str,
    ) -> list[dict[str, Any]]:
        """Parse a single table using the schema."""
        config = ScraperConfig(
            url=self._table_parser.url,
            section_id=section_id,
            expected_headers=["Grand Prix", "Circuit"],
            schema=schema,
            default_column=None,
            record_factory=record_from_mapping,
        )
        pipeline = TablePipeline(
            config=config,
            include_urls=self._table_parser._include_urls,
            normalize_empty_values=self._table_parser._options.normalize_empty_values,
        )
        return TableParsingHelper.parse_table_with_pipeline(table, pipeline)

    def _is_same_as_calendar(
        self,
        cancelled_data: list[dict[str, Any]],
        calendar_data: list[dict[str, Any]],
    ) -> bool:
        """
        Check if cancelled_rounds data is the same as calendar data.
        Compare based on grand_prix names and circuits.
        """
        if len(cancelled_data) != len(calendar_data):
            return False

        # Extract comparable fields (grand_prix and circuit)
        def extract_key_fields(data: list[dict[str, Any]]) -> list[tuple]:
            result = []
            for item in data:
                gp = item.get("grand_prix", {})
                circuit = item.get("circuit", {})

                # Extract text from grand_prix
                gp_text = gp.get("text", "") if isinstance(gp, dict) else str(gp)

                # Extract text from circuit (handle nested structure)
                if isinstance(circuit, dict):
                    # Circuit might be nested like {'circuit': {'text': '...', 'url': ...}}
                    circuit_inner = circuit.get("circuit", circuit)
                    if isinstance(circuit_inner, dict):
                        circuit_text = circuit_inner.get("text", "")
                    else:
                        circuit_text = str(circuit_inner)
                else:
                    circuit_text = str(circuit)

                result.append((gp_text, circuit_text))
            return result

        cancelled_fields = extract_key_fields(cancelled_data)
        calendar_fields = extract_key_fields(calendar_data)

        return cancelled_fields == calendar_fields
