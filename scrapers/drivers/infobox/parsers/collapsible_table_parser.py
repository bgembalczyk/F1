"""Helper class for parsing collapsible career tables from infobox cells."""

from typing import Any
from typing import Dict

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text


class CollapsibleTableParser:
    """Handles parsing of collapsible career statistics tables."""

    def __init__(self, cell_parser_delegate):
        """Initialize the collapsible table parser.
        
        Args:
            cell_parser_delegate: Delegate that provides methods for parsing cell values
                                 (parse_active_years, parse_teams, parse_int_cell, etc.)
        """
        self._delegate = cell_parser_delegate

    def parse_collapsible_career_table(self, table: Tag) -> Dict[str, Any] | None:
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

        # Extract the title from the first row
        title_row = table.find("tr")
        title = None
        if title_row:
            title_th = title_row.find("th")
            if title_th:
                title = clean_infobox_text(title_th.get_text(" ", strip=True))

        # Parse all label-value rows
        rows = []
        for tr in table.find_all("tr"):
            # Skip the title row
            th_cells = tr.find_all("th")
            td_cells = tr.find_all("td")

            # If we have one th and one td, it's a label-value pair
            if len(th_cells) == 1 and len(td_cells) == 1:
                label = clean_infobox_text(th_cells[0].get_text(" ", strip=True))
                value_cell = td_cells[0]

                # Parse value based on label
                if label in {"Active years", "Years active"}:
                    value = self._delegate.parse_active_years(value_cell)
                elif label == "Team":
                    value = self._delegate.parse_teams(value_cell)
                elif label in {"Starts", "Wins", "Podiums", "Points"}:
                    value = self._delegate.parse_int_cell(value_cell)
                elif label in {"First race", "Last race", "First win", "Last win"}:
                    value = self._delegate.parse_race_event(value_cell)
                else:
                    value = self._delegate.parse_cell(value_cell)

                rows.append({"label": label, "value": value})
            # If we have a full-width row with colspan=2, it might be a stats table
            elif len(td_cells) == 1 and td_cells[0].get("colspan") == "2":
                nested_table = td_cells[0].find("table")
                if nested_table:
                    table_data = self._delegate.parse_nested_table(nested_table)
                    rows.append({"table": table_data})

        return {"title": title, "rows": rows} if rows else None
