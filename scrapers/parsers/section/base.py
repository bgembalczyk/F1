from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.section.parse_results import SectionParseResult


class BaseSectionParser:
    """Canonical runtime base class for section parsers."""

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        """Parse section by delegating to ``parse_group`` when available."""
        parse_group = getattr(self, "parse_group", None)
        if callable(parse_group):
            return parse_group(list(section_fragment.children))
        msg = f"{self.__class__.__name__} must define parse() or parse_group()."
        raise NotImplementedError(msg)


__all__ = ["BaseSectionParser"]
