from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import strip_marks as strip_wiki_marks


def normalize_auto_value(
        value: Any,
        *,
        strip_marks: bool = False,
        drop_empty: bool = True,
) -> Any:
    if isinstance(value, dict):
        cleaned = dict(value)
        if strip_marks:
            cleaned["text"] = strip_wiki_marks(cleaned.get("text")) or ""
        if drop_empty and not (cleaned.get("text") or "").strip():
            return None
        return cleaned
    if isinstance(value, list):
        normalized = normalize_links(
            value,
            strip_marks=strip_marks,
            drop_empty=drop_empty,
        )
        if drop_empty and not normalized:
            return None
        return normalized
    if isinstance(value, str):
        cleaned = strip_wiki_marks(value) if strip_marks else value
        if drop_empty and not cleaned.strip():
            return None
        return cleaned
    return value
