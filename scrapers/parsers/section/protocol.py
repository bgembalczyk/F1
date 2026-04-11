from __future__ import annotations

import warnings
from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.parsers.section.base import BaseSectionParser
from scrapers.section.parse_results import SectionParseResult


class SectionParserProtocol(Protocol):
    """Typing-only contract for dependency injection and static checks."""

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult: ...


class SectionParser(BaseSectionParser):
    """Deprecated runtime alias. Use ``BaseSectionParser`` instead."""

    def __init_subclass__(cls, **kwargs):
        warnings.warn(
            "SectionParser is deprecated; inherit from BaseSectionParser instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init_subclass__(**kwargs)


__all__ = ["BaseSectionParser", "SectionParserProtocol", "SectionParser"]
