from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any

from layers.seed.data_classes import SeedQualityReport
from layers.seed.data_classes import SeedRecord
from scrapers.data_paths import DataPaths
from scrapers.data_paths import default_data_paths
from scrapers.wiki.contants import LINK_CANDIDATE_KEYS
from scrapers.wiki.contants import NAME_CANDIDATE_KEYS
from scrapers.wiki.contants import SEED_RECORD_SCHEMA_VERSION




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


def _resolve_seed_destination(
    *,
    output_root: Any,
    category: str,
    seed_name: str,
) -> Any:
    if isinstance(output_root, DataPaths):
        return output_root.raw_file(category, f"{seed_name}.json")
    output_path = output_root if output_root is not None else default_data_paths().raw
    return output_path / category / f"{seed_name}.json"


def write_seed_l0(
    *,
    records: list[dict[str, Any]],
    category: str,
    seed_name: str,
    output_root: Any,
) -> Any:
    destination = _resolve_seed_destination(
        output_root=output_root,
        category=category,
        seed_name=seed_name,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(records, ensure_ascii=False, indent=2)
    destination.write_text(payload, encoding="utf-8")
    return destination
