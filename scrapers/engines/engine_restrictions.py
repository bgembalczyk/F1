import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag

from models.validation.engine_restriction import EngineRestriction
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.table.columns.types.func import FuncColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.range import RangeColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.unit import UnitColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper
from scrapers.drivers.helpers.parsers import parse_engine_rpm_limit
from scrapers.drivers.helpers.parsers import parse_fuel_flow_rate
from scrapers.drivers.helpers.parsers import parse_fuel_injection_pressure_limit
from scrapers.drivers.helpers.parsers import parse_fuel_limit_per_race


class EngineRestrictionsScraper(F1TableScraper):
    """
    Ograniczenia silnikowe F1:
    https://en.wikipedia.org/wiki/Formula_One_regulations#Engine
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/Formula_One_regulations#Engine",
        section_id="Engine",
        expected_headers=["Year", "2000-2005", "2006-2013", "2014-2025"],
        model_class=EngineRestriction,
        column_map={
            "Year": "year",
            "Size": "size",
            "Type of engine": "type_of_engine",
            "Fuel-limit per race": "fuel_limit_per_race",
            "Fuel-flow rate": "fuel_flow_rate",
            "Fuel-injection pressure limit": "fuel_injection_pressure_limit",
            "Engine RPM limit": "engine_rpm_limit",
            "Power Output": "power_output",
        },
        columns={
            "year": SeasonsColumn(),
            "size": UnitColumn(unit="litre"),
            "type_of_engine": LinksListColumn(),
            "fuel_limit_per_race": FuncColumn(parse_fuel_limit_per_race),
            "fuel_flow_rate": FuncColumn(parse_fuel_flow_rate),
            "fuel_injection_pressure_limit": FuncColumn(
                parse_fuel_injection_pressure_limit
            ),
            "engine_rpm_limit": FuncColumn(parse_engine_rpm_limit),
            "power_output": RangeColumn(
                UnitColumn(unit="hp"),
                UnitColumn(unit="hp"),
                shared_suffix="hp",
            ),
        },
    )

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = HtmlTableParser(
            section_id=self.section_id,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )
        table = parser._find_table(soup)
        header_row = table.find("tr")
        if not header_row:
            raise RuntimeError("Nie znaleziono wiersza nagłówkowego w tabeli.")

        header_cells = header_row.find_all(["th", "td"])
        if len(header_cells) < 2:
            raise RuntimeError("Nagłówek tabeli jest niekompletny.")

        year_cells = header_cells[1:]

        rows = parser.parse(soup)
        row_labels: list[str] = []
        row_cells: list[list[Tag]] = []
        for row in rows:
            if not row.cells:
                continue
            label_cell = row.cells[0]
            label = clean_wiki_text(label_cell.get_text(" ", strip=True))
            row_labels.append(label)
            row_cells.append(row.cells[1:])

        headers = ["Year", *row_labels]
        records: list[dict[str, Any]] = []
        for index, year_cell in enumerate(year_cells):
            cells: list[Tag] = [year_cell]
            for cells_for_row in row_cells:
                if index < len(cells_for_row):
                    cells.append(cells_for_row[index])
                else:
                    cells.append(soup.new_tag("td"))
            record = self.pipeline.parse_cells(headers, cells, row_index=index)
            if record:
                records.append(record)

        return records


if __name__ == "__main__":
    run_and_export(
        EngineRestrictionsScraper,
        "engines/f1_engine_restrictions.json",
        "engines/f1_engine_restrictions.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
