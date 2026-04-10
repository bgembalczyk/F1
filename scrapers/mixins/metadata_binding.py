from __future__ import annotations

from typing import Any

from models.value_objects.common_terms import EntityName


class MetadataBindingMixin:
    """Metadata composition/binding helpers for section payload serialization."""

    @staticmethod
    def build_metadata(
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

    @staticmethod
    def bind_section_defaults(
        *,
        metadata: dict[str, Any],
        section_id: str,
        section_label: str,
    ) -> dict[str, Any]:
        bound = dict(metadata)
        bound.setdefault("parser", "unknown")
        bound.setdefault("source", "unknown")
        bound.setdefault("heading_path", [])
        bound.setdefault("section_id", section_id)
        bound.setdefault("section_label", EntityName.from_raw(section_label).to_export())
        return bound
