from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import Tag


def extract_text(element: Tag | None) -> str | None:
    """Extract normalized plain text from a tag."""
    if element is None:
        return None
    text = element.get_text(" ", strip=True)
    return text or None
