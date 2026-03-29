from __future__ import annotations

from dataclasses import asdict
from typing import Any

from models.value_objects.common_terms import EntityName
from models.value_objects.common_terms import SectionId
from scrapers.base.sections.interface import SectionParseResult


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


def build_section_parse_result(
    *,
    section_id: str,
    section_label: str,
    records: list[dict[str, Any]],
    parser: str,
    source: str,
    heading_path: tuple[str, ...] | None = None,
    extras: dict[str, Any] | None = None,
) -> SectionParseResult:
    return SectionParseResult(
        section_id=section_id,
        section_label=section_label,
        records=records,
        metadata=build_section_metadata(
            parser=parser,
            source=source,
            heading_path=heading_path,
            extras=extras,
        ),
    )


def normalize_section_metadata(
    section: SectionParseResult,
) -> dict[str, Any]:
    metadata = dict(section.metadata)
    metadata.setdefault("parser", "unknown")
    metadata.setdefault("source", "unknown")
    metadata.setdefault("heading_path", [])
    metadata.setdefault(
        "section_id",
        SectionId.from_raw(section.section_id).to_export(),
    )
    metadata.setdefault(
        "section_label",
        EntityName.from_raw(section.section_label).to_export(),
    )
    return metadata


def serialize_section_result(section: SectionParseResult) -> dict[str, Any]:
    payload = asdict(section)
    payload["section_id"] = SectionId.from_raw(section.section_id).to_export()
    payload["section_label"] = EntityName.from_raw(section.section_label).to_export()
    payload["metadata"] = normalize_section_metadata(section)
    return payload
