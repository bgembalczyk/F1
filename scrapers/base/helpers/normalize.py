from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.wiki import strip_marks as strip_wiki_marks


def normalize_auto_value(value: Any, *, strip_marks: bool = False) -> Any:
    if isinstance(value, dict):
        cleaned = dict(value)
        if strip_marks:
            cleaned["text"] = strip_wiki_marks(cleaned.get("text")) or ""
        return cleaned
    if isinstance(value, list):
        return normalize_links(value, strip_marks=strip_marks, drop_empty=True)
    if isinstance(value, str):
        return strip_wiki_marks(value) if strip_marks else value
    return value
