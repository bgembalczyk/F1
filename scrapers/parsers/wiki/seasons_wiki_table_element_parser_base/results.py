from typing import Any

from bs4 import BeautifulSoup

from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.constructor.constructor import ConstructorColumn
from scrapers.columns.types.driver import DriverColumn
from scrapers.columns.types.driver_list import DriverListColumn
from scrapers.columns.types.tyre import TyreColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.parsers.section.wiki.adapt import collect_section_elements
from scrapers.parsers.section.wiki.adapt import find_section_tree
from scrapers.parsers.wiki.body_content import BodyContentAssembler
from scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.base import BaseSeasonParser
from scrapers.orchestration.season_table_parsing_service import SeasonTableParsingService
from scrapers.table_schema_dsl import TableSchemaDSL
from scrapers.url_resolver import DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY


class SeasonResultsParser(BaseSeasonParser):
    def __init__(self, table_parser: SeasonTableParsingService) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup, season_year: int | None = None) -> list[dict[str, Any]]:
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
                ColumnSpec(
                    "Constructor",
                    "winning_constructor",
                    ConstructorColumn(),
                ),
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

        return self._table_parser.wiki_table_parser.parse(
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
        body = BodyContentAssembler.find_body_content(soup)
        if body is None:
            return []

        body_content = BodyContentAssembler().parse(body)
        article = body_content.get("content_text") or {}
        aliases = DEFAULT_URL_RESOLVER_STRATEGY_REGISTRY.section_aliases_for(
            domain="seasons",
            section_id="results",
        )
        target_section = find_section_tree(
            article,
            "Results",
            aliases,
            domain="seasons",
        )
        if not target_section:
            return []

        for table in collect_section_elements(target_section, "table"):
            rows = self._table_parser.table_payload_mapper.map(
                table.get("data", {}),
                expected_headers=expected_headers,
                schema=schema,
            )
            if rows:
                return rows
        return []


__all__ = ["SeasonResultsParser"]
