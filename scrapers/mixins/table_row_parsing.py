from __future__ import annotations

from collections.abc import Sequence

from bs4 import Tag

from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.text import clean_wiki_text


class TableRowParsingMixin:
    """Reusable table-row normalization helpers for HTML table parsers."""

    strip_lang_suffix: bool = True
    strip_refs: bool = True
    normalize_dashes: bool = True

    def _clean_cells(self, cells: Sequence[Tag]) -> list[str]:
        return [
            clean_wiki_text(
                c.get_text(" ", strip=True),
                strip_lang_suffix=self.strip_lang_suffix,
                strip_refs=self.strip_refs,
                normalize_dashes=self.normalize_dashes,
            )
            for c in cells
        ]

    @staticmethod
    def _is_empty_row(cells: Sequence[Tag]) -> bool:
        return not cells or all(not c.get_text(strip=True) for c in cells)

    @staticmethod
    def _is_repeated_header_row(cleaned_cells: Sequence[str], headers: Sequence[str]) -> bool:
        return is_repeated_header_row(cleaned_cells, headers)
