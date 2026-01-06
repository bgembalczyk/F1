from pathlib import Path
from typing import Any, List

from bs4 import BeautifulSoup, Tag

from models.validation.engine_regulation import EngineRegulation
from scrapers.base.helpers.multi_level_headers import MultiLevelHeaderBuilder
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.records import record_from_mapping
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.unit import UnitColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper
from scrapers.engines.columns.configuration import EngineConfigurationColumn
from scrapers.engines.columns.nested_text import NestedTextColumn
from scrapers.engines.columns.nested_unit_list import NestedUnitListColumn


class EngineRegulationScraper(F1TableScraper):
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

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/Formula_One_engines#Engine_regulation_progression_by_era",
        section_id="Engine_regulation_progression_by_era",
        expected_headers=["Years", "Operating principle"],
        model_class=EngineRegulation,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=record_from_mapping,
    )

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = HtmlTableParser(
            section_id=self.section_id,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )
        table = parser._find_table(soup)
        headers, header_rows = MultiLevelHeaderBuilder.build_headers(table)

        records: list[dict[str, Any]] = []
        pending_rowspans: dict[int, dict[str, object]] = {}
        rows = table.find_all("tr")[header_rows:]
        for row_index, tr in enumerate(rows):
            cells = tr.find_all(["td", "th"])
            if not cells or all(not cell.get_text(strip=True) for cell in cells):
                continue

            cleaned_cells = [
                clean_wiki_text(cell.get_text(" ", strip=True)) for cell in cells
            ]
            if parser._is_footer_row(cells, cleaned_cells, headers):
                continue
            if is_repeated_header_row(cleaned_cells, headers):
                continue

            expanded_cells = parser._expand_row_cells(
                cells,
                headers,
                pending_rowspans,
            )
            record = self.pipeline.parse_cells(
                headers, expanded_cells, row_index=row_index
            )
            if record:
                records.append(record)

        return records


if __name__ == "__main__":
    run_and_export(
        EngineRegulationScraper,
        "engines/f1_engine_regulations.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
