from __future__ import annotations

from abc import ABC

from bs4 import BeautifulSoup

from scrapers.domain_roles import Parser
from scrapers.section.parse_results import SectionParseResult


class SeasonSectionParser(Parser[BeautifulSoup, SectionParseResult], ABC):
    """Bazowy kontrakt parsera sekcji sezonowych."""


__all__ = ["SeasonSectionParser"]
