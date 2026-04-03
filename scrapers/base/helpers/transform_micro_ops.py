from __future__ import annotations

from typing import Any, TYPE_CHECKING

from models.domain_utils.field_normalization.aliases import (
    expand_alias_variants as _expand_alias_variants,
)

if TYPE_CHECKING:
    from collections.abc import Callable


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
    return _expand_alias_variants(values, text_normalizer=text_normalizer)
