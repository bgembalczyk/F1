from typing import Any

from bs4 import BeautifulSoup

from models.records.factories.mapping import MappingRecordFactory
from models.validation.engine.regulation import EngineRegulation
from scrapers.base_engine_table_scraper import BaseEngineTableScraper
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.configuration import EngineConfigurationColumn
from scrapers.columns.types.nested_text import NestedTextColumn
from scrapers.columns.types.nested_unit_list import NestedUnitListColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.text import TextColumn
from scrapers.columns.types.unit import UnitColumn
from scrapers.config_table import build_scraper_config
from scrapers.helpers.header import is_repeated_header_row
from scrapers.multi_level_header_builder import MultiLevelHeaderBuilder
from scrapers.parsers.section.protocol import SectionParser
from scrapers.parsers.section.sublevels import SubSectionParser
from scrapers.parsers.table.wiki.base import WikiTableBaseParser
from scrapers.source_catalog import ENGINE_PROGRESS
from scrapers.table_schema_dsl import TableSchemaDSL


class EngineRegulationTableParser(WikiTableBaseParser):
    table_type = "engine_regulation_progression"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Years": "seasons",
        "Operating principle": "operating_principle",
        "Maximum displacement - Naturally aspirated": "maximum_displacement",
        "Maximum displacement - Forced induction": "maximum_displacement",
        "Configuration": "configuration",
        "RPM limit": "rpm_limit",
        "Fuel flow limit (Qmax)": "fuel_flow_limit",
        "Fuel composition - Alcohol": "fuel_composition",
        "Fuel composition - Petrol": "fuel_composition",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Years", "Operating principle", "Configuration"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


TABLE_SCHEMA = TableSchemaDSL(
    columns=[
        ColumnSpec("Years", "seasons", SeasonsColumn()),
        ColumnSpec("Operating principle", "operating_principle", TextColumn()),
        ColumnSpec(
            "Maximum displacement - Naturally aspirated",
            "maximum_displacement",
            NestedUnitListColumn("naturally_aspirated"),
        ),
        ColumnSpec(
            "Maximum displacement - Forced induction",
            "maximum_displacement",
            NestedUnitListColumn("forced_induction"),
        ),
        ColumnSpec("Configuration", "configuration", EngineConfigurationColumn()),
        ColumnSpec("RPM limit", "rpm_limit", UnitColumn(unit="rpm")),
        ColumnSpec("Fuel flow limit (Qmax)", "fuel_flow_limit", TextColumn()),
        ColumnSpec(
            "Fuel composition - Alcohol",
            "fuel_composition",
            NestedTextColumn("alcohol"),
        ),
        ColumnSpec(
            "Fuel composition - Petrol",
            "fuel_composition",
            NestedTextColumn("petrol"),
        ),
    ],
)


class EngineRegulationSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = EngineRegulationTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_engine_regulation_table_parser(parsed)
        return parsed

    def _apply_engine_regulation_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_engine_regulation_table_parser(section)

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


class HistorySectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = EngineRegulationSubSectionParser()


class EngineRegulationScraper(BaseEngineTableScraper):
    """
    Regulacje silników F1 według ery:
    https://en.wikipedia.org/wiki/Formula_One_engines#Engine_regulation_progression_by_era
    """

    CONFIG = build_scraper_config(
        url=ENGINE_PROGRESS.url(),
        section_id=ENGINE_PROGRESS.section_id,
        expected_headers=["Years", "Operating principle"],
        model_class=EngineRegulation,
        schema=TABLE_SCHEMA,
        record_factory=MappingRecordFactory(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        parser = HistorySectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Parse multi-level header table with rowspan support."""
        table = self._find_table(soup)
        headers, header_rows = MultiLevelHeaderBuilder.build_headers(table)

        records: list[dict[str, Any]] = []
        pending_rowspans: dict[int, dict[str, object]] = {}
        rows = table.find_all("tr")[header_rows:]
        parser = self._create_parser()

        for row_index, tr in enumerate(rows):
            cells = tr.find_all(["td", "th"])
            cleaned_cells = self._clean_cells(cells)

            # Validate row
            if not self._is_valid_row(cells, cleaned_cells, headers):
                continue
            if is_repeated_header_row(cleaned_cells, headers):
                continue

            # Expand cells with rowspan handling
            expanded_cells = parser.expand_row_cells(
                cells,
                headers,
                pending_rowspans,
            )

            # Parse record
            record = self._parse_record(headers, expanded_cells, row_index)
            if record:
                records.append(record)

        return records
