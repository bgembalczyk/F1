from typing import Any

from bs4 import BeautifulSoup

from models.validation.engine_regulation import EngineRegulation
from scrapers.base.source_catalog import ENGINE_PROGRESS
from scrapers.base.helpers.multi_level_headers import MultiLevelHeaderBuilder
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.columns.types import UnitColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.engines.base_engine_table_scraper import BaseEngineTableScraper
from scrapers.engines.columns.configuration import EngineConfigurationColumn
from scrapers.engines.columns.nested_text import NestedTextColumn
from scrapers.engines.columns.nested_unit_list import NestedUnitListColumn


class EngineRegulationScraper(BaseEngineTableScraper):
    """
    Regulacje silników F1 według ery:
    https://en.wikipedia.org/wiki/Formula_One_engines#Engine_regulation_progression_by_era
    """

    schema_columns = [
        column("Years", "seasons", SeasonsColumn()),
        column("Operating principle", "operating_principle", TextColumn()),
        column(
            "Maximum displacement - Naturally aspirated",
            "maximum_displacement",
            NestedUnitListColumn("naturally_aspirated"),
        ),
        column(
            "Maximum displacement - Forced induction",
            "maximum_displacement",
            NestedUnitListColumn("forced_induction"),
        ),
        column("Configuration", "configuration", EngineConfigurationColumn()),
        column("RPM limit", "rpm_limit", UnitColumn(unit="rpm")),
        column("Fuel flow limit (Qmax)", "fuel_flow_limit", TextColumn()),
        column(
            "Fuel composition - Alcohol",
            "fuel_composition",
            NestedTextColumn("alcohol"),
        ),
        column(
            "Fuel composition - Petrol",
            "fuel_composition",
            NestedTextColumn("petrol"),
        ),
    ]

    CONFIG = build_scraper_config(
        url=ENGINE_PROGRESS.url(),
        section_id=ENGINE_PROGRESS.section_id,
        expected_headers=["Years", "Operating principle"],
        model_class=EngineRegulation,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=record_from_mapping,
    )

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


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
