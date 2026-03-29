from __future__ import annotations

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


def _extract_name_and_link(record: dict[str, Any]) -> tuple[str, str | None]:
    name = str(record.get("name") or "").strip()
    link = record.get("link")

    if not name and isinstance(record.get("driver"), dict):
        driver = record["driver"]
        name = str(driver.get("text") or "").strip()
        link = driver.get("url")

    return name, str(link).strip() if isinstance(link, str) else None


def normalize_seed_records(
    records: list[dict[str, Any]],
    *,
    source_url: str,
    scraped_at: datetime,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    scraped_iso = scraped_at.isoformat()
    for item in records:
        name, link = _extract_name_and_link(item)
        normalized.append(
            {
                "schema_version": SEED_RECORD_SCHEMA_VERSION,
                "name": name,
                "link": link,
                "source_url": source_url,
                "scraped_at": scraped_iso,
            },
        )
    return normalized


def compute_seed_quality(
    records: list[dict[str, Any]],
    *,
    seed_name: str,
    category: str,
) -> SeedQualityReport:
    _ = seed_name, category
    names: list[str] = []
    empty_name_count = 0
    empty_link_count = 0

    for record in records:
        name, link = _extract_name_and_link(record)
        if not name:
            empty_name_count += 1
        else:
            names.append(name.casefold())
        if not link:
            empty_link_count += 1

    duplicate_name_count = len(names) - len(set(names))
    return SeedQualityReport(
        records_count=len(records),
        empty_name_count=empty_name_count,
        empty_link_count=empty_link_count,
        duplicate_name_count=duplicate_name_count,
    )
