from __future__ import annotations

from dataclasses import dataclass

from bs4 import Tag

from scrapers.parsers.section.helpers import split_into_parts
from scrapers.parsers.section.located import LocatedSection


class SectionLocator:
    """Wyszukuje sekcje/fragmenty artykułu po poziomie nagłówka."""

    def locate(
        self, elements: list[Tag], *, heading_class: str
    ) -> list[LocatedSection]:
        return [
            LocatedSection(
                section_label=label,
                heading_anchor=anchor,
                elements=group_elements,
            )
            for label, anchor, group_elements in split_into_parts(
                elements, heading_class
            )
        ]


__all__ = ["SectionLocator"]
