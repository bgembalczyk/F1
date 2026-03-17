from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any

SEED_RECORD_SCHEMA_VERSION = "1.0"
NAME_CANDIDATE_KEYS = (
    "name",
    "driver",
    "constructor",
    "team",
    "circuit",
    "race_title",
    "season",
    "manufacturer",
)
LINK_CANDIDATE_KEYS = (
    "link",
    "url",
    "driver_url",
    "constructor_url",
    "team_url",
    "circuit_url",
)


@dataclass(frozen=True)
class SeedRecord:
    schema_version: str
    name: str
    link: str | None
    source_url: str
    scraped_at: str

    @classmethod
    def from_raw(
        cls,
        raw: dict[str, Any],
        *,
        source_url: str,
        scraped_at: datetime,
        schema_version: str = SEED_RECORD_SCHEMA_VERSION,
    ) -> "SeedRecord":
        return cls(
            schema_version=schema_version,
            name=_extract_name(raw),
            link=_extract_link(raw),
            source_url=source_url,
            scraped_at=scraped_at.astimezone(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    if isinstance(value, (int, float)):
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
