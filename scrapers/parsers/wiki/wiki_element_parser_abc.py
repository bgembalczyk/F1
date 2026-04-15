from __future__ import annotations

from typing import Literal

WikiElementType = Literal[
    "table",
    "list",
    "section",
    "infobox",
    "navbox",
    "references",
    "references_wrap",
    "paragraph",
    "figure",
    "article",
]


__all__ = [
    "WikiElementType",
]
