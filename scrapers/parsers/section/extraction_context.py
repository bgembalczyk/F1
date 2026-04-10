from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class SectionExtractionContext:
    """Shared context passed through every section parser layer."""

    page_title: str = ""
    page_url: str = ""
    breadcrumbs: tuple[str, ...] = ()
    html_metadata: dict[str, Any] | None = None
    section_id: str | None = None

    def with_section(
        self,
        *,
        section_name: str,
        section_id: str | None = None,
    ) -> SectionExtractionContext:
        return SectionExtractionContext(
            page_title=self.page_title,
            page_url=self.page_url,
            breadcrumbs=(*self.breadcrumbs, section_name),
            html_metadata=self.html_metadata,
            section_id=section_id,
        )
