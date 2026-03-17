from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from models.validation.engine_regulation import EngineRegulation
from scrapers.base.helpers.multi_level_headers import MultiLevelHeaderBuilder
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.records import record_from_mapping
from scrapers.base.run_config import RunConfig
from scrapers.engines.base_engine_table_scraper import BaseEngineTableScraper
from scrapers.engines.schemas import build_engine_regulation_schema
from scrapers.engines.spec import ENGINES_LIST_SPEC
from scrapers.engines.spec import build_engine_regulation_config


class EngineRegulationScraper(BaseEngineTableScraper):
    options_domain = ENGINES_LIST_SPEC.domain
    options_profile = ENGINES_LIST_SPEC.options_profile

    CONFIG = build_engine_regulation_config(
        expected_headers=["Years", "Operating principle"],
        model_class=EngineRegulation,
        schema=build_engine_regulation_schema(),
        record_factory=record_from_mapping,
    )

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
            expanded_cells = parser.expand_row_cells(cells, headers, pending_rowspans)
            record = self._parse_record(headers, expanded_cells, row_index)
            if record:
                records.append(record)

        return records


if __name__ == "__main__":
    run_and_export(
        EngineRegulationScraper,
        "engines/f1_engine_regulations.json",
        run_config=RunConfig(output_dir=Path("../../data/wiki"), include_urls=True),
    )
