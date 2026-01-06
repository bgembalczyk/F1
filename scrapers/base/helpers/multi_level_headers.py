"""Shared utility for building multi-level table headers."""

from typing import List

from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text


class MultiLevelHeaderBuilder:
    """Helper for building headers from multi-row table headers with colspan support."""

    @staticmethod
    def build_headers(table: Tag) -> tuple[List[str], int]:
        """Build headers from multi-row table headers.

        Handles tables with colspan in the first row and sub-headers in the second row.

        Args:
            table: BeautifulSoup Tag representing the table

        Returns:
            Tuple of (list of header strings, number of header rows)

        Raises:
            RuntimeError: If no header rows found
        """
        header_rows: List[Tag] = []
        # First try to find headers in thead
        thead = table.find("thead")
        if thead:
            header_rows = thead.find_all("tr")

        # If not found in thead, search for rows with th elements
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
