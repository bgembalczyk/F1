from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.sections.constants import DOMAIN_SECTION_ALIASES
from scrapers.base.table.columns.types import DriverColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.sections.adapter import collect_section_elements
from scrapers.wiki.parsers.sections.adapter import find_section_tree


class SeasonResultsParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        expected_headers = [
            "Round",
            "Fastest lap",
            "Winning driver",
            "Report",
        ]
        schema = TableSchemaDSL(
            columns=[
                ColumnSpec("Round", "round", IntColumn()),
                ColumnSpec("Grand Prix", "grand_prix", UrlColumn()),
                ColumnSpec("Race", "grand_prix", UrlColumn()),
                ColumnSpec("Pole position", "pole_position", DriverColumn()),
                ColumnSpec("Pole Position", "pole_position", DriverColumn()),
                ColumnSpec("Fastest lap", "fastest_lap", DriverListColumn()),
                ColumnSpec("Winning driver", "winning_driver", DriverColumn()),
                ColumnSpec(
                    "Winning constructor",
                    "winning_constructor",
                    ConstructorColumn(),
                ),
                ColumnSpec("Constructor", "winning_constructor", ConstructorColumn()),
                ColumnSpec("Report", "report", UrlColumn()),
                ColumnSpec("Tyre", "tyre", TyreColumn()),
            ],
        )

        by_adapter = self._parse_from_content_tree(
            soup,
            expected_headers=expected_headers,
            schema=schema,
        )
        if by_adapter:
            return by_adapter

        return self._table_parser.parse_table(
            soup,
            section_ids=["Grands_Prix", "Results_and_standings"],
            expected_headers=expected_headers,
            schema=schema,
        )

    def _parse_from_content_tree(
        self,
        soup: BeautifulSoup,
        *,
        expected_headers: list[str],
        schema: TableSchemaDSL,
    ) -> list[dict[str, Any]]:
        body = BodyContentParser.find_body_content(soup)
        if body is None:
            return []

        body_content = BodyContentParser().parse(body)
        article = body_content.get("content_text") or {}
        aliases = DOMAIN_SECTION_ALIASES.get("seasons", {}).get("results", set())
        target_section = find_section_tree(
            article,
            "Results",
            aliases,
            domain="seasons",
        )
        if not target_section:
            return []

        for table in collect_section_elements(target_section, "table"):
            rows = self._table_parser.parse_table_data(
                table.get("data", {}),
                expected_headers=expected_headers,
                schema=schema,
            )
            if rows:
                return rows
        return []
