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
        for candidate in [row.get("style"), row.get("bgcolor")]:
            color = self._extract_color(candidate)
            if color:
                return color
        for cell in row.find_all(["th", "td"], recursive=False):
            for candidate in [cell.get("style"), cell.get("bgcolor")]:
                color = self._extract_color(candidate)
                if color:
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
