from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class SectionParseResult:
    """Unified output for domain section parsers."""

    section_id: str
    section_label: str
    records: list[dict[str, Any]]
    metadata: dict[str, Any]


class SectionParser(Protocol):
    """Common section parser interface.

    Input: BeautifulSoup fragment scoped to a section.
    Output: parsed records with section-level metadata.
    """

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        ...
