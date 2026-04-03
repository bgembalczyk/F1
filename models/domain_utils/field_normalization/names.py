from __future__ import annotations

from typing import Any


def normalize_name(value: Any) -> str | None:
    """Normalize a single name-like field to a stripped string."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def add_unique_name(
    seen_names: set[str],
    names: list[str],
    value: Any,
) -> None:
    """Append normalized name if it is non-empty and not already present."""
    normalized = normalize_name(value)
    if normalized is None:
        return
    key = normalized.lower()
    if key in seen_names:
        return
    seen_names.add(key)
    names.append(normalized)
