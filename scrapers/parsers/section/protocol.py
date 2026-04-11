from __future__ import annotations

from scrapers.parsers.roles import SectionParserABC
from scrapers.parsers.section.base import BaseSectionParser


class SectionParser(BaseSectionParser, SectionParserABC):
    """Bazowa klasa parserów sekcji dla modułów domenowych."""


__all__ = ["BaseSectionParser", "SectionParserABC", "SectionParser"]
