from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import strip_marks as strip_wiki_marks


def normalize_auto_value(
    value: Any,
    *,
    strip_marks: bool = False,
    drop_empty: bool = True,
) -> Any:
    result: Any = value

    if isinstance(value, dict):
        cleaned = dict(value)
        if strip_marks:
            cleaned["text"] = strip_wiki_marks(cleaned.get("text")) or ""
        result = cleaned
        if drop_empty and not (cleaned.get("text") or "").strip():
            result = None
    elif isinstance(value, list):
        normalized = normalize_links(
            value,
            strip_marks=strip_marks,
            drop_empty=drop_empty,
        )
        result = None if drop_empty and not normalized else normalized
    elif isinstance(value, str):
        cleaned = strip_wiki_marks(value) if strip_marks else value
        result = None if drop_empty and not cleaned.strip() else cleaned

    return result
