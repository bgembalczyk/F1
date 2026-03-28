from __future__ import annotations

from dataclasses import asdict
from typing import Any

from scrapers.base.sections.interface import SectionParseResult

SECTION_METADATA_CONTRACT_KEYS = ("parser", "source", "heading_path")


def build_section_metadata(
    *,
    parser: str,
    source: str,
    heading_path: tuple[str, ...] | None = None,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "parser": parser,
        "source": source,
        "heading_path": list(heading_path) if heading_path else [],
    }
    if extras:
        metadata.update(extras)
    return metadata


def normalize_section_metadata(
    section: SectionParseResult,
) -> dict[str, Any]:
    metadata = dict(section.metadata)
    metadata.setdefault("parser", "unknown")
    metadata.setdefault("source", "unknown")
    metadata.setdefault("heading_path", [])
    metadata.setdefault("section_id", section.section_id)
    metadata.setdefault("section_label", section.section_label)
    return metadata


def serialize_section_result(section: SectionParseResult) -> dict[str, Any]:
    payload = asdict(section)
    payload["metadata"] = normalize_section_metadata(section)
    return payload


def export_section_records_by_id(
    sections: list[SectionParseResult],
) -> dict[str, list[dict[str, Any]]]:
    return {section.section_id: section.records for section in sections}
