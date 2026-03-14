"""Shared utility for building multi-level table headers."""

from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text


class MultiLevelHeaderBuilder:
    """Helper for building headers from multi-row table headers with colspan support."""

    @staticmethod
    def _get_header_rows(table: Tag) -> list[Tag]:
        thead = table.find("thead")
        if thead:
            rows = thead.find_all("tr")
            if rows:
                return rows

        rows: list[Tag] = []
        for row in table.find_all("tr"):
            has_th = bool(row.find_all("th"))
            has_td = bool(row.find_all("td"))
            if has_th and not has_td:
                rows.append(row)
                continue
            if has_td:
                break
        return rows

    @staticmethod
    def _colspan(cell: Tag) -> int:
        try:
            return int(cell.get("colspan", 1))
        except ValueError:
            return 1

    @staticmethod
    def build_headers(table: Tag) -> tuple[list[str], int]:
        """Build headers from multi-row table headers.

        Handles tables with colspan in the first row and sub-headers in the second row.
        """
        header_rows = MultiLevelHeaderBuilder._get_header_rows(table)
        if not header_rows:
            msg = "Nie znaleziono nagłówków tabeli."
            raise RuntimeError(msg)

        first_row_cells = header_rows[0].find_all(["th", "td"])
        second_row_cells = (
            header_rows[1].find_all(["th", "td"])
            if len(header_rows) > 1
            else []
        )
        second_iter = iter(second_row_cells)

        headers: list[str] = []
        for cell in first_row_cells:
            text = clean_wiki_text(cell.get_text(" ", strip=True))
            colspan = MultiLevelHeaderBuilder._colspan(cell)
            if colspan <= 1:
                headers.append(text)
                continue

            for _ in range(colspan):
                sub_cell = next(second_iter, None)
                sub_text = None
                if sub_cell is not None:
                    sub_text = clean_wiki_text(sub_cell.get_text(" ", strip=True))
                headers.append(f"{text} - {sub_text}" if sub_text else text)

        return headers, len(header_rows)
