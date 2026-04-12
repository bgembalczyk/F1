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
from scrapers.parsers.section.history import HistorySectionParser
from scrapers.source_catalog import ENGINE_PROGRESS
from scrapers.table_schema_dsl import TableSchemaDSL

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


class EngineRegulationScraper(BaseEngineTableScraper):
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
        table = self._find_table(soup)
        headers, header_rows = MultiLevelHeaderBuilder.build_headers(table)

        records: list[dict[str, Any]] = []
        pending_rowspans: dict[int, dict[str, object]] = {}
        rows = table.find_all("tr")[header_rows:]
        parser = self._create_parser()

        for row_index, tr in enumerate(rows):
            cells = tr.find_all(["td", "th"])
            cleaned_cells = self._clean_cells(cells)
            if not self._is_valid_row(cells, cleaned_cells, headers):
                continue
            if is_repeated_header_row(cleaned_cells, headers):
                continue

            expanded_cells = parser.expand_row_cells(
                cells,
                headers,
                pending_rowspans,
            )
            record = self._parse_record(headers, expanded_cells, row_index)
            if record:
                records.append(record)

        return records


__all__ = ["EngineRegulationScraper", "TABLE_SCHEMA"]
