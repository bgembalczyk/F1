from __future__ import annotations

from typing import Optional, Dict, List, Any
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup

from scrapers.base.table.helpers.utils import clean_wiki_text, extract_links_from_cell
from scrapers.base.table.scraper import F1TableScraper


class _CircuitTableScraper(F1TableScraper):
    """Lekki scraper pojedynczej tabeli Wikipedii z zamianą linków na absolutne."""

    def __init__(
        self,
        *,
        table: Tag,
        base_url: str,
        index: int,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(include_urls=True, session=session, headers=headers)
        self._table = table
        self._base_url = base_url
        self._index = index

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        return urljoin(self._base_url, href)

    def _find_table(self, soup: BeautifulSoup) -> Tag:
        # Ignorujemy `soup` – wiemy już, którą tabelę parsować
        return self._table

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table = self._find_table(soup)
        header_row = table.find("tr")
        headers: List[str] = []
        if header_row:
            headers = [
                clean_wiki_text(c.get_text(" ", strip=True))
                for c in header_row.find_all(["th", "td"])
            ]

        rows: List[List[Dict[str, Any]]] = []
        for tr in table.find_all("tr")[1:]:
            cells = tr.find_all(["td", "th"])
            if not cells or all(not c.get_text(strip=True) for c in cells):
                continue

            # sprawdzamy, czy to nie jest "footer" powtarzający nagłówki
            cleaned_cells = [
                clean_wiki_text(c.get_text(" ", strip=True)) for c in cells
            ]
            if (
                headers
                and len(cleaned_cells) == len(headers)
                and cleaned_cells == headers
            ):
                continue

            row: List[Dict[str, Any]] = []
            for cell in cells:
                text = clean_wiki_text(cell.get_text(" ", strip=True))
                links = extract_links_from_cell(cell, full_url=self._full_url)
                row.append({"text": text, "links": links})
            rows.append(row)

        caption = table.find("caption")
        caption_text = (
            clean_wiki_text(caption.get_text(" ", strip=True)) if caption else None
        )

        return [
            {
                "index": self._index,
                "caption": caption_text,
                "headers": headers,
                "rows": rows,
            }
        ]
