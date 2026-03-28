from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.sections.constants import DOMAIN_SECTION_ALIASES
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import UrlColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.constructor import ConstructorColumn
from scrapers.seasons.columns.driver import DriverColumn
from scrapers.seasons.columns.driver_list import DriverListColumn
from scrapers.seasons.columns.tyre import TyreColumn
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.section_adapter import collect_section_elements
from scrapers.wiki.parsers.section_adapter import find_section_tree


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
                column("Round", "round", IntColumn()),
                column("Grand Prix", "grand_prix", UrlColumn()),
                column("Race", "grand_prix", UrlColumn()),
                column("Pole position", "pole_position", DriverColumn()),
                column("Pole Position", "pole_position", DriverColumn()),
                column("Fastest lap", "fastest_lap", DriverListColumn()),
                column("Winning driver", "winning_driver", DriverColumn()),
                column(
                    "Winning constructor",
                    "winning_constructor",
                    ConstructorColumn(),
                ),
                column("Constructor", "winning_constructor", ConstructorColumn()),
                column("Report", "report", UrlColumn()),
                column("Tyre", "tyre", TyreColumn()),
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
