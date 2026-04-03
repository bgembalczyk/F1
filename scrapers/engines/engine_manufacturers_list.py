from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.validation.engine_manufacturer import EngineManufacturer
from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.base.source_catalog import ENGINES_LIST
from scrapers.base.table.builders import build_base_stats_columns
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_entity_metadata_columns
from scrapers.base.table.builders import build_name_status_fragment
from scrapers.base.table.builders import entity_column
from scrapers.base.table.columns.types import FloatColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper
from scrapers.engines.columns.manufacturer_name_status import (
    EngineManufacturerNameStatusColumn,
)
from scrapers.wiki.parsers.elements.list import ListParser
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class EngineManufacturersTableParser(WikiTableBaseParser):
    table_type = "engine_manufacturers_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Manufacturer": "manufacturer",
        "Engines built in": "engines_built_in",
        "Seasons": "seasons",
        "Races Entered": "races_entered",
        "Races Started": "races_started",
        "Wins": "wins",
        "Points": "points",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Manufacturer", "Engines built in", "Seasons", "Wins"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }

    @staticmethod
    def build_schema() -> TableSchemaDSL:
        return TableSchemaDSL(
            columns=build_columns(
                build_name_status_fragment(
                    header="Manufacturer",
                    output_key="manufacturer",
                    column_type=EngineManufacturerNameStatusColumn(),
                ),
                build_entity_metadata_columns(
                    [
                        entity_column(
                            "Engines built in",
                            "engines_built_in",
                            LinksListColumn(),
                        ),
                    ],
                ),
                build_base_stats_columns(column_overrides={"points": FloatColumn()}),
            ),
        )


class IndianapolisOnlyListParser(ListParser):
    def parse(self, element: Tag) -> dict[str, list[dict[str, str]]]:
        items: list[dict[str, str]] = []
        for li in element.find_all("li", recursive=False):
            anchor = li.find("a")
            manufacturer = li.get_text(" ", strip=True)
            if not manufacturer:
                continue
            row: dict[str, str] = {"manufacturer": manufacturer}
            if anchor and anchor.has_attr("href"):
                row["manufacturer_url"] = anchor["href"]
            items.append(row)
        return {"items": items}


class IndianapolisOnlySubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._list_parser = IndianapolisOnlyListParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_indianapolis_only_list_parser(parsed)
        return parsed

    def _apply_indianapolis_only_list_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_indianapolis_only_list_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_indianapolis_only_list_parser(item)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "list":
                continue
            raw_html = element.get("raw_html_fragment")
            if not isinstance(raw_html, str):
                continue
            parsed_tag = BeautifulSoup(raw_html, "html.parser").find(["ul", "ol"])
            if isinstance(parsed_tag, Tag):
                element["data"] = self._list_parser.parse(parsed_tag)


class EngineManufacturersSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = IndianapolisOnlySubSectionParser()
        self._table_parser = EngineManufacturersTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_engine_table_parser(parsed)
        return parsed

    def _apply_engine_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_engine_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_engine_table_parser(item)

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


class EngineManufacturersListScraper(F1TableScraper):
    """
    Lista konstruktorów silników F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers#Engine_manufacturers
    """

    CONFIG = build_scraper_config(
        url=ENGINES_LIST.base_url,
        # sekcja z główną tabelą
        section_id=ENGINES_LIST.section_id,
        # wystarczy podzbiór nagłówków żeby znaleźć właściwą tabelę
        expected_headers=[
            "Manufacturer",
            "Engines built in",
            "Seasons",
            "Races Entered",
            "Races Started",
            "Wins",
            "Points",
        ],
        record_factory=RECORD_FACTORIES.builders("engine_manufacturer"),
        model_class=EngineManufacturer,
        schema=EngineManufacturersTableParser.build_schema(),
    )

    _SUPPORTED_EXPORT_SCOPES = {"all", "engine_manufacturers", "indianapolis_only"}

    def __init__(
        self,
        *args: Any,
        export_scope: str = "all",
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = (
                f"Unsupported export_scope='{export_scope}' for "
                f"{self.__class__.__name__}"
            )
            raise ValueError(msg)
        self._export_scope = export_scope
        parser = EngineManufacturersSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if self._export_scope == "indianapolis_only":
            selector = WikipediaSectionByIdSelectionStrategy(domain="engines")
            section = selector.extract_section_by_id(
                soup,
                ENGINES_LIST.section_id,
                domain="engines",
            )
            if section is None:
                return []
            parsed = self.section_parser.parse(section)
            return self._extract_indianapolis_only_records(parsed)
        return super()._parse_soup(soup)

    def _extract_indianapolis_only_records(
        self,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        self._visit_indianapolis_sections(payload, records)
        return records

    def _visit_indianapolis_sections(
        self,
        node: dict[str, Any],
        records: list[dict[str, Any]],
    ) -> None:
        for section in self._iter_sub_sections(node):
            self._visit_indianapolis_sections(section, records)
        for element in node.get("elements", []):
            records.extend(self._extract_element_records(element))

    @staticmethod
    def _iter_sub_sections(node: dict[str, Any]) -> list[dict[str, Any]]:
        sections: list[dict[str, Any]] = []
        for key in ("sub_sections", "sub_sub_sections", "sub_sub_sub_sections"):
            value = node.get(key, [])
            if isinstance(value, list):
                sections.extend(
                    section for section in value if isinstance(section, dict)
                )
        return sections

    def _extract_element_records(self, element: Any) -> list[dict[str, Any]]:
        if not isinstance(element, dict) or element.get("kind") != "list":
            return []
        data = element.get("data")
        if not isinstance(data, dict):
            return []
        items = data.get("items", [])
        if not isinstance(items, list):
            return []
        return [
            self._normalize_indianapolis_record(item)
            for item in items
            if isinstance(item, dict)
        ]

    def _normalize_indianapolis_record(self, item: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(item)
        if not self.include_urls:
            normalized.pop("manufacturer_url", None)
            return normalized
        url = normalized.get("manufacturer_url")
        if isinstance(url, str) and url.startswith("/"):
            normalized["manufacturer_url"] = self._full_url(url)
        return normalized


class IndianapolisOnlyEngineManufacturersListScraper(IndianapolisOnlyListScraper):
    url = ENGINES_LIST.base_url
    record_key = "manufacturer"
    url_key = "manufacturer_url"
    domain_name = "engines"
    record_type = "manufacturer"
