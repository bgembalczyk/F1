from typing import Any


def normalize_iso(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    return normalize_text(value)


def normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
