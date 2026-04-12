from dataclasses import dataclass

from bs4 import Tag


@dataclass(frozen=True)
class LocatedSection:
    section_label: str
    heading_anchor: str | None
    elements: list[Tag]
