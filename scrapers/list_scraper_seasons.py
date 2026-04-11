"""DEPRECATED ENTRYPOINT: use scrapers.seasons.entrypoint.run_list_scraper."""

import warnings

from scrapers.builders_table import build_columns
from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.config_table import TableScraperConfig
from scrapers.config_table import build_scraper_config
from scrapers.options import ScraperOptions
from scrapers.parsers.section.protocol import SectionParser
from scrapers.parsers.table.wiki.base import WikiTableBaseParser
from scrapers.seed_list_scraper_table import SeedListTableScraper
from scrapers.source_catalog import SEASONS_LIST
from scrapers.table_schema_dsl import TableSchemaDSL

warnings.warn(
    "list_scraper_seasons is deprecated; use scrapers.seasons_list_scraper.",
    DeprecationWarning,
    stacklevel=2,
)


from typing import Any

from scrapers.adapters.factories.dataclass import RECORD_FACTORIES


class SeasonsTableParser(WikiTableBaseParser):
    table_type = "seasons_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Season": "season",
        "Races": "races",
        "Countries": "countries",
        "First": "first",
        "Last": "last",
        "Drivers' Champion (team)": "drivers_champion_team",
        "Constructors' Champion": "constructors_champion",
        "Winners": "winners",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Season", "Races"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


TABLE_SCHEMA = TableSchemaDSL(
    columns=build_columns(
        ColumnSpec("Season", "season", UrlColumn()),
        ColumnSpec("Races", "races", IntColumn()),
        ColumnSpec("Countries", "countries", IntColumn()),
        ColumnSpec("First", "first", UrlColumn()),
        ColumnSpec("Last", "last", UrlColumn()),
        ColumnSpec(
            "Drivers' Champion (team)",
            "drivers_champion_team",
            LinksListColumn(),
        ),
        ColumnSpec(
            "Constructors' Champion",
            "constructors_champion",
            LinksListColumn(),
        ),
        ColumnSpec("Winners", "winners", IntColumn()),
    ),
)


class SeasonsSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = SeasonsTableParser()

    def parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_seasons_table_parser(parsed)
        return parsed

    def _apply_seasons_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_seasons_table_parser(section)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed


class SeasonsListScraper(SeedListTableScraper):
    domain = "seasons"

    """
    Scraper listy sezonów z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_seasons
    (główna tabela World Championship seasons)
    """

    CONFIG = build_scraper_config(
        url=SEASONS_LIST.base_url,
        # jeśli id sekcji się kiedyś zmieni - poprawiasz tylko to
        section_id=SEASONS_LIST.section_id,
        # nagłówki, które MUSZĄ wystąpić w tabeli
        expected_headers=[
            "Season",
            "Races",
        ],
        schema=TABLE_SCHEMA,
        record_factory=RECORD_FACTORIES.builders("season_summary"),
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: TableScraperConfig | None = None,
    ) -> None:
        super().__init__(options=options, config=config)
        parser = SeasonsSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser
