from pathlib import Path
from typing import Any, List

from bs4 import BeautifulSoup, Tag

from models.validation.engine_regulation import EngineRegulation
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.nested_text import NestedTextColumn
from scrapers.base.table.columns.types.nested_unit_list import NestedUnitListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.unit import UnitColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper


class EngineRegulationScraper(F1TableScraper):
    """
    Regulacje silników F1 według ery:
    https://en.wikipedia.org/wiki/Formula_One_engines#Engine_regulation_progression_by_era
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/Formula_One_engines#Engine_regulation_progression_by_era",
        section_id="Engine_regulation_progression_by_era",
        expected_headers=["Years", "Operating principle"],
        model_class=EngineRegulation,
        column_map={
            "Years": "seasons",
            "Operating principle": "operating_principle",
            "Maximum displacement - Naturally aspirated": "maximum_displacement",
            "Maximum displacement - Forced induction": "maximum_displacement",
            "Configuration": "configuration",
            "RPM limit": "rpm_limit",
            "Fuel flow limit (Qmax)": "fuel_flow_limit",
            "Fuel composition - Alcohol": "fuel_composition",
            "Fuel composition - Petrol": "fuel_composition",
        },
        columns={
            "seasons": SeasonsColumn(),
            "operating_principle": TextColumn(),
            "Maximum displacement - Naturally aspirated": NestedUnitListColumn(
                "naturally_aspirated"
            ),
            "Maximum displacement - Forced induction": NestedUnitListColumn(
                "forced_induction"
            ),
            "configuration": EngineConfigurationColumn(),
            "rpm_limit": UnitColumn(unit="rpm"),
            "fuel_flow_limit": TextColumn(),
            "Fuel composition - Alcohol": NestedTextColumn("alcohol"),
            "Fuel composition - Petrol": NestedTextColumn("petrol"),
        },
    )

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        parser = HtmlTableParser(
            section_id=self.section_id,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )
        table = parser._find_table(soup)
        headers, header_rows = self._build_headers(table)

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

    @staticmethod
    def _build_headers(table: Tag) -> tuple[List[str], int]:
        header_rows: List[Tag] = []
        for row in table.find_all("tr"):
            if row.find_all("th"):
                header_rows.append(row)
                continue
            if row.find_all("td"):
                break

        if not header_rows:
            raise RuntimeError("Nie znaleziono nagłówków tabeli.")

        first_row_cells = header_rows[0].find_all(["th", "td"])
        second_row_cells: List[Tag] = []
        if len(header_rows) > 1:
            second_row_cells = header_rows[1].find_all(["th", "td"])

        second_iter = iter(second_row_cells)
        headers: List[str] = []
        for cell in first_row_cells:
            text = clean_wiki_text(cell.get_text(" ", strip=True))
            try:
                colspan = int(cell.get("colspan", 1))
            except ValueError:
                colspan = 1

            if colspan > 1:
                for _ in range(colspan):
                    sub_text = None
                    if second_row_cells:
                        try:
                            sub_cell = next(second_iter)
                            sub_text = clean_wiki_text(
                                sub_cell.get_text(" ", strip=True)
                            )
                        except StopIteration:
                            sub_text = None
                    if sub_text:
                        headers.append(f"{text} - {sub_text}")
                    else:
                        headers.append(text)
            else:
                headers.append(text)

        return headers, len(header_rows)


if __name__ == "__main__":
    run_and_export(
        EngineRegulationScraper,
        "engines/f1_engine_regulations.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
from scrapers.engines.columns.configuration import EngineConfigurationColumn
