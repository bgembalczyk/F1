from typing import Any

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.options import ScraperOptions
from scrapers.base.source_catalog import TYRES
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.tyres.columns.append_links import AppendLinksColumn
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class TyreManufacturersBySeasonTableParser(WikiTableBaseParser):
    table_type = "tyre_manufacturers_by_season"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Season": "seasons",
        "Manufacturer 1": "manufacturers",
        "Manufacturer 2": "manufacturers",
        "Manufacturer 3": "manufacturers",
        "Manufacturer 4": "manufacturers",
        "Manufacturer 5": "manufacturers",
        "Manufacturer 6": "manufacturers",
        "Wins": "wins",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Season", "Manufacturer 1", "Wins"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


class TyreManufacturersBySeasonSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = TyreManufacturersBySeasonTableParser()

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


class ManufacturersSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = TyreManufacturersBySeasonSubSectionParser()


class TyreManufacturersScraper(F1TableScraper):
    """
    Scraper producentów opon F1:
    https://en.wikipedia.org/wiki/Formula_One_tyres#Tyre_manufacturers_by_season
    """

    schema_columns = [
        column("Season", "seasons", SeasonsColumn()),
        column("Manufacturer 1", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 2", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 3", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 4", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 5", "manufacturers", AppendLinksColumn()),
        column("Manufacturer 6", "manufacturers", AppendLinksColumn()),
        column("Wins", "wins", SkipColumn()),
    ]

    CONFIG = build_scraper_config(
        url=TYRES.url(),
        section_id=TYRES.section_id,
        expected_headers=[
            "Season",
            "Manufacturer 1",
            "Wins",
        ],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=RECORD_FACTORIES.mapping(),
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        super().__init__(options=options, config=config)
        parser = ManufacturersSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser


TyreManufacturersBySeasonScraper = TyreManufacturersScraper


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
