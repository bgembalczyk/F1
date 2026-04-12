"""DEPRECATED ENTRYPOINT: use scrapers.grands_prix.entrypoint.run_list_scraper."""

import warnings

from scrapers.builders_table import EntityColumnSpec
from scrapers.builders_table import build_columns
from scrapers.builders_table import build_entity_metadata_columns
from scrapers.builders_table import build_name_status_fragment
from scrapers.columns.factory import IntColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.multi.name_status_column.race_title_status import (
    RaceTitleStatusColumn,
)
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.config_table import build_scraper_config
from scrapers.mixins.apply_for_elements import ApplyForElementsMixin
from scrapers.options import ScraperOptions
from scrapers.parsers.wiki.nested_wiki import NestedWikiSectionParser
from scrapers.parsers.table.wiki.base import WikiTableBaseParser
from scrapers.parsers.wiki.sublevels.sub_section import SubSectionParser
from scrapers.seed_list_scraper_table import SeedListTableScraper
from scrapers.source_catalog import GRANDS_PRIX_LIST
from scrapers.table_schema_dsl import TableSchemaDSL

warnings.warn(
    "list_scraper_grands_prix is deprecated; use scrapers.grands_prix_list_scraper.",
    DeprecationWarning,
    stacklevel=2,
)


from typing import Any

from scrapers.adapters.factories.dataclass import RECORD_FACTORIES


class GrandsPrixTableParser(WikiTableBaseParser):
    table_type = "grands_prix_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Race title": "race_title",
        "Country": "country",
        "Years held": "years_held",
        "Circuits": "circuits",
        "Total": "total",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Race title", "Years held"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


TABLE_SCHEMA = TableSchemaDSL(
    columns=build_columns(
        build_name_status_fragment(
            header="Race title",
            output_key="race_title",
            column_type=RaceTitleStatusColumn(),
        ),
        build_entity_metadata_columns(
            [
                EntityColumnSpec("Country", "country", LinksListColumn()),
                EntityColumnSpec("Years held", "years_held", SeasonsColumn()),
                EntityColumnSpec("Circuits", "circuits", IntColumn()),
                EntityColumnSpec("Total", "total", IntColumn()),
            ],
        ),
    ),
)


class ByRaceTitleSubSectionParser(SubSectionParser, ApplyForElementsMixin):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = GrandsPrixTableParser()

    def _parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super()._parse_group(elements, context=context)
        self._apply_table_parser_to_sections(parsed, "sub_sub_sections")
        return parsed


class RacesSectionParser(NestedWikiSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = ByRaceTitleSubSectionParser()


class GrandsPrixListScraper(SeedListTableScraper):
    domain = "grands_prix"
    output_basename = "f1_grands_prix_extended.json"

    """
    Uproszczony scraper np. dla tabeli 'By race title'
    z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix
    """

    CONFIG = build_scraper_config(
        url=GRANDS_PRIX_LIST.base_url,
        section_id=GRANDS_PRIX_LIST.section_id,
        # podzbiór nagłówków - do znalezienia właściwej tabeli
        expected_headers=[
            "Race title",
            "Years held",
        ],
        schema=TABLE_SCHEMA,
        record_factory=RECORD_FACTORIES.builders("grands_prix"),
    )

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        parser = RacesSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser
