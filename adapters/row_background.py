from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import Tag


class HtmlRowBackgroundColorAdapter:
    """Technical adapter for extracting normalized background colors from HTML rows."""

    _background_hex = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})")
    _short_hex_len = 3

    def extract(self, row: Tag) -> str | None:
        if (style := row.get("style")) and (color := self._extract_color(style)):
            return color
        if (bgcolor := row.get("bgcolor")) and (color := self._extract_color(bgcolor)):
            return color

        for cell in row.children:
            if cell.name in ("th", "td"):
                if (style := cell.get("style")) and (
                    color := self._extract_color(style)
                ):
                    return color
                if (bgcolor := cell.get("bgcolor")) and (
                    color := self._extract_color(bgcolor)
                ):
                    return color
        return None

    def _extract_color(self, candidate: str | None) -> str | None:
        if not candidate:
            return None
        match = self._background_hex.search(candidate)
        if not match:
            return None
        normalized = match.group(1).lower()
        if len(normalized) == self._short_hex_len:
            return "".join(ch * 2 for ch in normalized)
        return normalized
