from __future__ import annotations

from collections.abc import Callable
from typing import Any


def pop_list_field(record: dict[str, Any], key: str) -> list[Any]:
    """Pop a key from record and normalize the value into a list."""
    value = record.pop(key, [])
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def merge_unique_preserve_order(*iterables: list[Any]) -> list[Any]:
    """Merge multiple lists preserving first occurrence order."""
    merged: list[Any] = []
    seen: set[Any] = set()
    for iterable in iterables:
        for item in iterable:
            if item in seen:
                continue
            seen.add(item)
            merged.append(item)
    return merged


def expand_alias_variants(
    values: set[str],
    *,
    text_normalizer: Callable[[str], str],
) -> tuple[set[str], set[str]]:
    """Build normalized section-text and id variants from alias values."""
    normalized_texts = {
        text_normalizer(value)
        for value in values
        if isinstance(value, str) and value.strip()
    }
    normalized_ids = {
        variant
        for text in normalized_texts
        for variant in (text.replace(" ", "_"), text)
    }
    return normalized_ids, normalized_texts
