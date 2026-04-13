from __future__ import annotations

from dataclasses import asdict
from typing import Any

from models.entity_name import EntityName
from models.section_id import SectionId
from scrapers.mixins.metadata_binding import MetadataBindingMixin
from scrapers.section.parse_results import SectionParseResult


_SECTION_METADATA_BINDER = MetadataBindingMixin()


def build_section_metadata(
    *,
    parser: str,
    source: str,
    heading_path: tuple[str, ...] | None = None,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _SECTION_METADATA_BINDER.build_metadata(
        parser=parser,
        source=source,
        heading_path=heading_path,
        extras=extras,
    )


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
    return _SECTION_METADATA_BINDER.bind_section_defaults(
        metadata=dict(section.metadata),
        section_id=str(section.section_id),
        section_label=EntityName.from_raw(section.section_label).to_export(),
    )


def serialize_section_result(section: SectionParseResult) -> dict[str, Any]:
    payload = asdict(section)
    payload["section_id"] = str(section.section_id)
    payload["section_label"] = EntityName.from_raw(section.section_label).to_export()
    payload["metadata"] = normalize_section_metadata(section)
    return payload


def coerce_section_parse_result(
    payload: SectionParseResult | dict[str, Any] | list[dict[str, Any]],
    *,
    default_section_id: str,
    default_section_label: str,
    parser: str,
    source: str = "legacy",
) -> SectionParseResult:
    if isinstance(payload, SectionParseResult):
        return payload

    if isinstance(payload, list):
        return build_section_parse_result(
            section_id=default_section_id,
            section_label=default_section_label,
            records=[item for item in payload if isinstance(item, dict)],
            parser=parser,
            source=source,
            extras={"legacy_payload": True},
        )

    if not isinstance(payload, dict):
        msg = "Section parser contract violation: parser output is not serializable."
        raise TypeError(msg)

    records_raw = payload.get("records")
    if records_raw is None:
        records_raw = payload.get("items", [])
    records = records_raw if isinstance(records_raw, list) else []
    metadata = payload.get("metadata")
    return SectionParseResult(
        section_id=SectionId.from_raw(payload.get("section_id", default_section_id)),
        section_label=EntityName.from_raw(
            payload.get(
                "section_label",
                payload.get("section", default_section_label),
            ),
        ),
        records=[item for item in records if isinstance(item, dict)],
        metadata={
            **build_section_metadata(
                parser=parser,
                source=source,
                extras={"legacy_payload": True},
            ),
            **(metadata if isinstance(metadata, dict) else {}),
        },
    )
