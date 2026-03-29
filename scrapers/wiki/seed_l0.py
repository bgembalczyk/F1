from scrapers.wiki.constants import SEED_RECORD_SCHEMA_VERSION
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SeedQualityReport:
    records_count: int
    empty_name_count: int
    empty_link_count: int
    duplicate_name_count: int


def normalize_seed_records(
    records: list[dict[str, Any]],
    *,
    source_url: str,
    scraped_at: datetime,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        if "name" in record or "link" in record:
            name = str(record.get("name") or "").strip()
            link = record.get("link")
        else:
            first_dict = next((value for value in record.values() if isinstance(value, dict)), {})
            name = str(first_dict.get("text") or "").strip()
            link = first_dict.get("url")
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
    _ = (seed_name, category)
    names = [str(record.get("name") or "").strip() for record in records]
    non_empty = [name for name in names if name]
    return SeedQualityReport(
        records_count=len(records),
        empty_name_count=sum(1 for name in names if not name),
        empty_link_count=sum(1 for record in records if not record.get("link")),
        duplicate_name_count=len(non_empty) - len(set(non_empty)),
    )

__all__ = [
    "SEED_RECORD_SCHEMA_VERSION",
    "SeedQualityReport",
    "compute_seed_quality",
    "normalize_seed_records",
]
