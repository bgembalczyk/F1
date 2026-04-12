from typing import Any

from bs4 import BeautifulSoup

from models.validation.engine.manufacturer import EngineManufacturer
from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.builders_table import EntityColumnSpec
from scrapers.builders_table import build_base_stats_columns
from scrapers.builders_table import build_columns
from scrapers.builders_table import build_entity_metadata_columns
from scrapers.builders_table import build_name_status_fragment
from scrapers.columns.factory import FloatColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.multi.name_status_column.engine_manufacturer import (
    EngineManufacturerNameStatusColumn,
)
from scrapers.config_table import build_scraper_config
from scrapers.parsers.wiki.base_nested_section.sub_section.engine_manufacturers_indianapolis import EngineManufacturersIndianapolisSubSectionParser
from scrapers.scraper_table import F1TableScraper
from scrapers.section.selection_strategy import WikipediaSectionByIdSelectionStrategy
from scrapers.source_catalog import ENGINES_LIST
from scrapers.table_schema_dsl import TableSchemaDSL

TABLE_SCHEMA = TableSchemaDSL(
    columns=build_columns(
        build_name_status_fragment(
            header="Manufacturer",
            output_key="engine_constructor",
            column_type=EngineManufacturerNameStatusColumn(),
        ),
        build_entity_metadata_columns(
            [
                EntityColumnSpec(
                    "Engines built in",
                    "engines_built_in",
                    LinksListColumn(),
                ),
            ],
        ),
        build_base_stats_columns(column_overrides={"points": FloatColumn()}),
    ),
)


class EngineManufacturersListScraper(F1TableScraper):
    CONFIG = build_scraper_config(
        url=ENGINES_LIST.base_url,
        section_id=ENGINES_LIST.section_id,
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
        schema=TABLE_SCHEMA,
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
        parser = EngineManufacturersIndianapolisSubSectionParser()
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
        payload: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        if not isinstance(payload, dict):
            return []
        records: list[dict[str, Any]] = []
        self._visit_indianapolis_sections(payload, records)
        return records

    def _visit_indianapolis_sections(
        self,
        node: dict[str, Any] | None,
        records: list[dict[str, Any]],
    ) -> None:
        if not isinstance(node, dict):
            return
        for section in self._iter_sub_sections(node):
            self._visit_indianapolis_sections(section, records)
        for element in node.get("elements", []):
            records.extend(self._extract_element_records(element))

    @staticmethod
    def _iter_sub_sections(node: dict[str, Any] | None) -> list[dict[str, Any]]:
        if not isinstance(node, dict):
            return []
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
            self.normalize_indianapolis_record(item)
            for item in items
            if isinstance(item, dict)
        ]

    def normalize_indianapolis_record(self, item: dict[str, Any]) -> dict[str, Any]:
        return self._normalize_indianapolis_record(item)

    def _normalize_indianapolis_record(self, item: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(item)
        engine_constructor = normalized.get("engine_constructor")
        if isinstance(engine_constructor, str):
            normalized["engine_constructor"] = engine_constructor.strip()
        return normalized


__all__ = ["EngineManufacturersListScraper", "TABLE_SCHEMA"]
