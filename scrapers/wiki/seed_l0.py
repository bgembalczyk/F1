from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any
from typing import TYPE_CHECKING

from models.contracts.seed import SEED_RECORD_SCHEMA_VERSION
from models.contracts.seed import SeedRecord

if TYPE_CHECKING:
    from scrapers.config import DataPaths


@dataclass(frozen=True)
class SeedQualityReport:
    seed_name: str
    category: str
    records_count: int
    empty_name_count: int
    empty_link_count: int
    duplicate_name_count: int

    def to_log_line(self) -> str:
        return (
            "[seed-quality] "
            f"seed={self.seed_name} "
            f"category={self.category} "
            f"records={self.records_count} "
            f"empty_name={self.empty_name_count} "
            f"empty_link={self.empty_link_count} "
            f"duplicate_name={self.duplicate_name_count}"
        )


def normalize_seed_records(
    records: list[dict[str, Any]],
    *,
    source_url: str,
    scraped_at: datetime | None = None,
) -> list[dict[str, Any]]:
    ts = scraped_at or datetime.now(tz=timezone.utc)
    return [
        SeedRecord.from_raw(record, source_url=source_url, scraped_at=ts).to_dict()
        for record in records
    ]


def compute_seed_quality(
    records: list[dict[str, Any]],
    *,
    seed_name: str,
    category: str,
) -> SeedQualityReport:
    names = [str(item.get("name") or "").strip() for item in records]
    links = [item.get("link") for item in records]

    non_empty_names = [name.casefold() for name in names if name]
    duplicate_name_count = len(non_empty_names) - len(set(non_empty_names))

    return SeedQualityReport(
        seed_name=seed_name,
        category=category,
        records_count=len(records),
        empty_name_count=sum(1 for name in names if not name),
        empty_link_count=sum(1 for link in links if not link),
        duplicate_name_count=duplicate_name_count,
    )


def write_seed_l0(
    *,
    records: list[dict[str, Any]],
    category: str,
    seed_name: str,
    output_root: Any,
) -> Any:
    from scrapers.config import DataPaths
    from scrapers.config import default_data_paths

    if isinstance(output_root, DataPaths):
        destination = output_root.raw_file(category, f"{seed_name}.json")
    else:
        output_path = (
            output_root if output_root is not None else default_data_paths().raw
        )
        destination = output_path / category / f"{seed_name}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(records, ensure_ascii=False, indent=2)
    destination.write_text(payload, encoding="utf-8")
    return destination
