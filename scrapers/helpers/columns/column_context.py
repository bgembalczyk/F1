from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from bs4 import Tag

from scrapers.helpers.f1_table_utils import clean_wiki_text


@dataclass
class ColumnContext:
    """
    Kontekst pojedynczej komórki tabeli.

    - udostępnia cell (Tag),
    - leniwie wylicza raw_text / clean_text,
    - niesie helper do budowania pełnego URL,
    - niesie sentinel _SKIP z F1TableScraper.
    """

    header: str
    key: str
    cell: Tag
    include_urls: bool
    full_url: Callable[[str | None], str | None]
    skip_sentinel: object

    @property
    def raw_text(self) -> str:
        return self.cell.get_text(" ", strip=True)

    @property
    def clean_text(self) -> str:
        return clean_wiki_text(self.raw_text)
