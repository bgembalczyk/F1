"""DEPRECATED ENTRYPOINT: use scrapers.grands_prix.entrypoint.run_list_scraper."""

from typing import Any

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.options import ScraperOptions
from scrapers.base.source_catalog import GRANDS_PRIX_LIST
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_entity_metadata_columns
from scrapers.base.table.builders import build_name_status_fragment
from scrapers.base.table.builders import entity_column
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
from scrapers.grands_prix.columns.race_title_status import RaceTitleStatusColumn
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


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
                entity_column("Country", "country", LinksListColumn()),
                entity_column("Years held", "years_held", SeasonsColumn()),
                entity_column("Circuits", "circuits", IntColumn()),
                entity_column("Total", "total", IntColumn()),
            ],
        ),
    ),
)


class ByRaceTitleSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = GrandsPrixTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_table_parser(parsed)
        return parsed

    def _apply_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_table_parser(section)

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


class RacesSectionParser(SectionParser):
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
