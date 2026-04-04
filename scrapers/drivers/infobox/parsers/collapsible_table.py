"""Helper class for parsing collapsible career tables from infobox cells."""

from typing import Any

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.numeric import NumericParser
from scrapers.drivers.infobox.parsers.table import TableParser


class CollapsibleTableParser:
    """Handles parsing of collapsible career statistics tables."""

    def __init__(self, cell_parser_delegate):
        """Initialize the collapsible table parser.

        Args:
            cell_parser_delegate: Delegate that provides methods for parsing cell values
                                 (parse_active_years, parse_teams, parse_int_cell, etc.)
        """
        self._delegate = cell_parser_delegate

    def parse_collapsible_career_table(self, table: Tag) -> dict[str, Any] | None:
        """Parse collapsible career statistics table (e.g., motorcycle racing).

        Example structure:
        <table class="mw-collapsible">
          <tr><th>Title</th></tr>
          <tr><th>Active years</th><td>1960-1964</td></tr>
          <tr><th>Starts</th><td>129</td></tr>
          ...
        </table>

        Args:
            table: BeautifulSoup Tag representing the collapsible table

        Returns:
            Dictionary with 'title' and 'rows' keys, or None if table is empty
        """
        if not table:
            return None

        title = self._extract_title(table)
        rows = self._parse_rows(table)
        return {"title": title, "rows": rows} if rows else None

    def _extract_title(self, table: Tag) -> str | None:
        title_row = table.find("tr")
        if not title_row:
            return None
        title_th = title_row.find("th")
        if not title_th:
            return None
        return clean_infobox_text(title_th.get_text(" ", strip=True))

    def _parse_rows(self, table: Tag) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for tr in table.find_all("tr"):
            parsed = self._parse_table_row(tr)
            if parsed is not None:
                rows.append(parsed)
        return rows

    def _parse_table_row(self, tr: Tag) -> dict[str, Any] | None:
        th_cells = tr.find_all("th")
        td_cells = tr.find_all("td")

        if len(th_cells) == 1 and len(td_cells) == 1:
            return self._parse_label_value_row(th_cells[0], td_cells[0])
        if len(td_cells) == 1 and td_cells[0].get("colspan") == "2":
            return self._parse_nested_table_row(td_cells[0])
        return None

    def _parse_label_value_row(self, th_cell: Tag, value_cell: Tag) -> dict[str, Any]:
        label = clean_infobox_text(th_cell.get_text(" ", strip=True))
        value = self._parse_value_for_label(label, value_cell)
        return {"label": label, "value": value}

    def _parse_value_for_label(self, label: str | None, value_cell: Tag) -> Any:
        if label in {"Active years", "Years active"}:
            return self._delegate.parse_active_years(value_cell)
        if label == "Team":
            return self._delegate.parse_teams(value_cell)
        if label in {"Starts", "Wins", "Podiums", "Points"}:
            return NumericParser.parse_int_cell(value_cell)
        if label in {"First race", "Last race", "First win", "Last win"}:
            return self._delegate.parse_race_event(value_cell)
        return self._delegate.parse_cell(value_cell)

    def _parse_nested_table_row(self, cell: Tag) -> dict[str, Any] | None:
        nested_table = cell.find("table")
        if not nested_table:
            return None
        table_data = TableParser.parse_nested_table(nested_table)
        return {"table": table_data}
