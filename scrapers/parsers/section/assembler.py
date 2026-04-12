from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.parsers.section.detection import make_stable_section_id
from scrapers.parsers.section.extraction_context import SectionExtractionContext


@dataclass(frozen=True)
class SectionAssembler:
    """Składa wynik sekcji z ujednoliconymi metadanymi."""

    def assemble(
        self,
        *,
        section_name: str,
        heading_anchor: str | None,
        context: SectionExtractionContext,
        fragment: dict[str, Any],
    ) -> dict[str, Any]:
        section_id = make_stable_section_id(
            heading_anchor=heading_anchor,
            heading_text=section_name,
            breadcrumbs=context.breadcrumbs,
        )
        return {
            "section_label": section_name,
            "section_id": section_id,
            **fragment,
        }


__all__ = ["SectionAssembler"]
