from __future__ import annotations

import warnings
from typing import Protocol

from bs4 import BeautifulSoup

from scrapers.parsers.section.base import BaseSectionParser
from scrapers.section.parse_results import SectionParseResult


class SectionParserProtocol(Protocol):
    """Typing-only protocol for section parser collaborators."""

    def parse(self, fragment: BeautifulSoup) -> SectionParseResult: ...


class LegacySectionParser(BaseSectionParser):
    """Deprecated runtime alias kept for safe migration."""

    def __init_subclass__(cls, **kwargs):
        warnings.warn(
            "LegacySectionParser is deprecated; inherit from BaseSectionParser instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init_subclass__(**kwargs)


__all__ = ["SectionParserProtocol", "LegacySectionParser"]
