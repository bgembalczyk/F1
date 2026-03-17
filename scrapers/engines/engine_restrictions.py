from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.validation.engine_restriction import EngineRestriction
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.run_config import RunConfig
from scrapers.engines.base_engine_table_scraper import BaseEngineTableScraper
from scrapers.engines.schemas import build_engine_restrictions_schema
from scrapers.engines.spec import ENGINES_LIST_SPEC
from scrapers.engines.spec import build_engine_restrictions_config


class EngineRestrictionsScraper(BaseEngineTableScraper):
    options_domain = ENGINES_LIST_SPEC.domain
    options_profile = ENGINES_LIST_SPEC.options_profile

    CONFIG = build_engine_restrictions_config(
        expected_headers=["Year", "2000-2005", "2006-2013", "2014-2025"],
        record_factory=EngineRestriction,
        schema=build_engine_restrictions_schema(),
    )

    def _parse_soup(self, soup: BeautifulSoup) -> list[Any]:
        table = self._find_table(soup)
        header_row = table.find("tr")
        if not header_row:
            raise RuntimeError("Nie znaleziono wiersza nagłówkowego w tabeli.")
        header_cells = header_row.find_all(["th", "td"])
        if len(header_cells) < 2:
            raise RuntimeError("Nagłówek tabeli jest niekompletny.")

        year_cells = header_cells[1:]
        parser = self._create_parser()
        rows = parser.parse(soup)
        row_labels: list[str] = []
        row_cells: list[list[Tag]] = []
        for row in rows:
            if not row.cells:
                continue
            label_cell = row.cells[0]
            label = self._clean_cells([label_cell])[0]
            row_labels.append(label)
            row_cells.append(row.cells[1:])

        headers = ["Year", *row_labels]
        records: list[Any] = []
        for index, year_cell in enumerate(year_cells):
            cells: list[Tag] = [year_cell]
            for cells_for_row in row_cells:
                cells.append(cells_for_row[index] if index < len(cells_for_row) else soup.new_tag("td"))
            record = self._parse_record(headers, cells, index)
            if record:
                records.append(record)
        return records


if __name__ == "__main__":
    run_and_export(
        EngineRestrictionsScraper,
        "engines/f1_engine_restrictions.json",
        run_config=RunConfig(output_dir=Path("../../data/wiki"), include_urls=True),
    )
