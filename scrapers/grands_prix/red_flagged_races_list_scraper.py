from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.func import FuncColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.scraper import F1TableScraper


def _restart_status(ctx: ColumnContext) -> Dict[str, Any] | None:
    text = (ctx.clean_text or "").strip()
    if not text:
        return None
    code = text[0].upper()
    mapping = {
        "N": "race_was_not_restarted",
        "Y": "race_was_restarted_over_original_distance",
        "R": "race_was_resumed_to_complete_original_distance",
        "S": "race_was_restarted_or_resumed_without_completing_original_distance",
    }
    return {"code": code, "description": mapping.get(code)}


class _RedFlaggedRacesBaseScraper(F1TableScraper):
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

    def fetch(self) -> List[Dict[str, Any]]:
        rows = super().fetch()
        for row in rows:
            drivers = row.pop("failed_to_make_restart_drivers", None)
            reason = row.pop("failed_to_make_restart_reason", None)
            if drivers is None and reason is None:
                continue
            row["failed_to_make_restart"] = {
                "drivers": drivers or [],
                "reason": reason,
            }
        return rows


class RedFlaggedWorldChampionshipRacesScraper(_RedFlaggedRacesBaseScraper):
    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_red-flagged_Formula_One_races",
        section_id="Red-flagged_races",
        expected_headers=[
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
            "Failed to make the restart",
        ],
        column_map={
            "Year": "season",
            "Grand Prix": "grand_prix",
            "Lap": "lap",
            "R": "restart_status",
            "Winner": "winner",
            "Incident that prompted red flag": "incident",
            "Failed to make the restart - Drivers": "failed_to_make_restart_drivers",
            "Failed to make the restart - Reason": "failed_to_make_restart_reason",
            "Ref.": "ref",
        },
        columns={
            "season": IntColumn(),
            "grand_prix": UrlColumn(),
            "lap": IntColumn(),
            "restart_status": FuncColumn(_restart_status),
            "winner": DriverColumn(),
            "incident": TextColumn(),
            "failed_to_make_restart_drivers": DriverListColumn(),
            "failed_to_make_restart_reason": TextColumn(),
            "ref": SkipColumn(),
        },
    )


class RedFlaggedNonChampionshipRacesScraper(_RedFlaggedRacesBaseScraper):
    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_red-flagged_Formula_One_races",
        section_id="Non-championship_races",
        expected_headers=[
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
            "Failed to make the restart",
        ],
        column_map={
            "Year": "season",
            "Grand Prix": "grand_prix",
            "Lap": "lap",
            "R": "restart_status",
            "Winner": "winner",
            "Incident that prompted red flag": "incident",
            "Failed to make the restart - Drivers": "failed_to_make_restart_drivers",
            "Failed to make the restart - Reason": "failed_to_make_restart_reason",
            "Ref.": "ref",
        },
        columns={
            "season": IntColumn(),
            "grand_prix": UrlColumn(),
            "lap": IntColumn(),
            "restart_status": FuncColumn(_restart_status),
            "winner": DriverColumn(),
            "incident": TextColumn(),
            "failed_to_make_restart_drivers": DriverListColumn(),
            "failed_to_make_restart_reason": TextColumn(),
            "ref": SkipColumn(),
        },
    )


if __name__ == "__main__":
    run_and_export(
        RedFlaggedWorldChampionshipRacesScraper,
        "grands_prix/f1_red_flagged_world_championship_races.json",
        "grands_prix/f1_red_flagged_world_championship_races.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
    run_and_export(
        RedFlaggedNonChampionshipRacesScraper,
        "grands_prix/f1_red_flagged_non_championship_races.json",
        "grands_prix/f1_red_flagged_non_championship_races.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
