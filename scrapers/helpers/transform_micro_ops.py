from __future__ import annotations

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
