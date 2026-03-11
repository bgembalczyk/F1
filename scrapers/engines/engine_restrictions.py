from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.validation.engine_restriction import EngineRestriction
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.range import RangeColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.unit import UnitColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL
from scrapers.base.table.dsl import column
from scrapers.engines.base_engine_table_scraper import BaseEngineTableScraper
from scrapers.engines.columns.engine_rpm_limit import EngineRpmLimitColumn
from scrapers.engines.columns.fuel_flow_rate import FuelFlowRateColumn
from scrapers.engines.columns.fuel_injection_pressure_limit import (
    FuelInjectionPressureLimitColumn,
)
from scrapers.engines.columns.fuel_limit_per_race import FuelLimitPerRaceColumn


class EngineRestrictionsScraper(BaseEngineTableScraper):
    """
    Ograniczenia silnikowe F1:
    https://en.wikipedia.org/wiki/Formula_One_regulations#Engine
    """

    schema_columns = [
        column("Year", "year", SeasonsColumn()),
        column("Size", "size", UnitColumn(unit="litre")),
        column("Type of engine", "type_of_engine", LinksListColumn()),
        column("Fuel-limit per race", "fuel_limit_per_race", FuelLimitPerRaceColumn()),
        column("Fuel-flow rate", "fuel_flow_rate", FuelFlowRateColumn()),
        column(
            "Fuel-injection pressure limit",
            "fuel_injection_pressure_limit",
            FuelInjectionPressureLimitColumn(),
        ),
        column("Engine RPM limit", "engine_rpm_limit", EngineRpmLimitColumn()),
        column(
            "Power Output",
            "power_output",
            RangeColumn(
                UnitColumn(unit="hp"),
                UnitColumn(unit="hp"),
                shared_suffix="hp",
            ),
        ),
    ]

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/Formula_One_regulations#Engine",
        section_id="Engine",
        expected_headers=["Year", "2000-2005", "2006-2013", "2014-2025"],
        record_factory=EngineRestriction,
        schema=TableSchemaDSL(columns=schema_columns),
    )

    def _parse_soup(self, soup: BeautifulSoup) -> list[Any]:
        """Parse transposed table where years are columns and metrics are rows."""
        table = self._find_table(soup)
        header_row = table.find("tr")
        if not header_row:
            raise RuntimeError("Nie znaleziono wiersza nagłówkowego w tabeli.")

        header_cells = header_row.find_all(["th", "td"])
        if len(header_cells) < 2:
            raise RuntimeError("Nagłówek tabeli jest niekompletny.")

        year_cells = header_cells[1:]

        # Parse rows to extract labels and cells
        parser = self._create_parser()
        rows = parser.parse(soup)
        row_labels: list[str] = []
        row_cells: list[list[Tag]] = []
        for row in rows:
            if not row.cells:
                continue
            label_cell = row.cells[0]
            cleaned_cells = self._clean_cells([label_cell])
            label = cleaned_cells[0]
            row_labels.append(label)
            row_cells.append(row.cells[1:])

        # Build records by transposing: each year becomes a record
        headers = ["Year", *row_labels]
        records: list[Any] = []
        for index, year_cell in enumerate(year_cells):
            cells: list[Tag] = [year_cell]
            for cells_for_row in row_cells:
                if index < len(cells_for_row):
                    cells.append(cells_for_row[index])
                else:
                    cells.append(soup.new_tag("td"))
            record = self._parse_record(headers, cells, index)
            if record:
                records.append(record)

        return records


if __name__ == "__main__":
    run_and_export(
        EngineRestrictionsScraper,
        "engines/f1_engine_restrictions.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
