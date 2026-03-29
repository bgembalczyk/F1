from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from scrapers.wiki.constants import SEED_RECORD_SCHEMA_VERSION


@dataclass(frozen=True)
class SeedQualityReport:
    records_count: int
    empty_name_count: int
    empty_link_count: int
    duplicate_name_count: int
    seed_name: str
    category: str


def _extract_name_and_link(record: dict[str, Any]) -> tuple[str, str | None]:
    for key in ("name", "driver", "constructor", "circuit", "season", "grand_prix"):
        value = record.get(key)
        if isinstance(value, dict):
            return str(value.get("text") or "").strip(), value.get("url")
        if key == "name" and isinstance(value, str):
            return value.strip(), record.get("link")
    return str(record.get("name") or "").strip(), record.get("link")


def normalize_seed_records(
    records: list[dict[str, Any]],
    *,
    source_url: str,
    scraped_at: datetime,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        name, link = _extract_name_and_link(record)
        normalized.append(
            {
                "schema_version": SEED_RECORD_SCHEMA_VERSION,
                "name": name,
                "link": link,
                "source_url": source_url,
                "scraped_at": scraped_at.isoformat(),
            },
        )
    return normalized


def compute_seed_quality(
    records: list[dict[str, Any]],
    *,
    seed_name: str,
    category: str,
) -> SeedQualityReport:
    names = [str(record.get("name") or "").strip() for record in records]
    links = [record.get("link") for record in records]
    counts = Counter(name for name in names if name)
    return SeedQualityReport(
        records_count=len(records),
        empty_name_count=sum(1 for name in names if not name),
        empty_link_count=sum(1 for link in links if not link),
        duplicate_name_count=sum(1 for value in counts.values() if value > 1),
        seed_name=seed_name,
        category=category,
    )
