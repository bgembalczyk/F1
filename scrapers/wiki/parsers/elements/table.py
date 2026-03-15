from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser


class TableParser(WikiParser):
    """Parser tabel wikitable Wikipedii.

    Przetwarza tabelę: <table class="wikitable">
    """

    def parse(self, element: Tag) -> dict[str, Any]:
        """Parsuje tabelę wikitable HTML.

        Args:
            element: Element <table class="wikitable">.

        Returns:
            Słownik z nagłówkami i wierszami tabeli.
        """
        headers: list[str] = []
        rows: list[list[str]] = []

        header_row = element.find("tr")
        if header_row:
            headers = [
                th.get_text(" ", strip=True)
                for th in header_row.find_all(["th", "td"])
            ]

        for tr in element.find_all("tr")[1:]:
            cells = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)

        return {"headers": headers, "rows": rows}
