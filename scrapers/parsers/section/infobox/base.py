from __future__ import annotations

from abc import ABC

from scrapers.parsers.section.base import SectionParserBase


class InfoboxSectionParser(SectionParserBase, ABC):
    """Base class for section parsers extracting infobox payloads."""


__all__ = ["InfoboxSectionParser"]
