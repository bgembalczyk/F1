from __future__ import annotations

from abc import ABC

from scrapers.parsers.section.base import SectionParserBase


class ListSectionParser(SectionParserBase, ABC):
    """Base class for section parsers whose primary source is HTML lists."""


__all__ = ["ListSectionParser"]
