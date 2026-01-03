from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.records import ExportRecord
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers import RecordTransformer


class FailedToMakeRestartTransformer(RecordTransformer):
    def transform(self, records: List[ExportRecord]) -> List[ExportRecord]:
        for row in records:
            drivers = row.pop("failed_to_make_restart_drivers", None)
            reason = row.pop("failed_to_make_restart_reason", None)
            if drivers is None and reason is None:
                continue
            row["failed_to_make_restart"] = {
                "drivers": drivers or [],
                "reason": reason,
            }
        return records


class RedFlaggedRacesBaseScraper(F1TableScraper):
    def __init__(self, *, options=None, config=None) -> None:
        super().__init__(options=options, config=config)
        self.transformers = [FailedToMakeRestartTransformer()]

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
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
        thead = table.find("thead")
        if thead:
            header_rows = thead.find_all("tr")

        if not header_rows:
            for row in table.find_all("tr"):
                has_th = bool(row.find_all("th"))
                has_td = bool(row.find_all("td"))
                if has_th and not has_td:
                    header_rows.append(row)
                    continue
                if has_td:
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
