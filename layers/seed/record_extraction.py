from __future__ import annotations

from typing import Any

from scrapers.wiki.constants import LINK_CANDIDATE_KEYS
from scrapers.wiki.constants import NAME_CANDIDATE_KEYS


def _extract_name(record: dict[str, Any]) -> str:
    for key in NAME_CANDIDATE_KEYS:
        value = record.get(key)
        text = _coerce_text(value)
        if text:
            return text
    return ""


def _extract_link(record: dict[str, Any]) -> str | None:
    for key in LINK_CANDIDATE_KEYS:
        value = record.get(key)
        link = _coerce_link(value)
        if link:
            return link

    for key in NAME_CANDIDATE_KEYS:
        value = record.get(key)
        link = _coerce_link(value)
        if link:
            return link
    return None


def _coerce_text(value: Any) -> str:
    if isinstance(value, dict):
        nested_text = value.get("text") or value.get("name")
        return str(nested_text).strip() if nested_text else ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, int | float):
        return str(value)
    return ""


def _coerce_link(value: Any) -> str | None:
    if isinstance(value, dict):
        nested_link = value.get("url") or value.get("link")
        return str(nested_link).strip() if nested_link else None
    if isinstance(value, str):
        candidate = value.strip()
        return candidate if candidate.startswith("http") else None
    return None
