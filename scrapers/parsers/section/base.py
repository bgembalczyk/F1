from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.section.parse_results import SectionParseResult


class BaseSectionParser(ABC):
    """Canonical runtime base class for section parsers."""

    @abstractmethod
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        """Parse a section fragment into the canonical section parse result."""


__all__ = ["BaseSectionParser"]
