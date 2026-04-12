from __future__ import annotations

from abc import ABC

from scrapers.parsers.section.base import SectionParserBase


class TextBlockSectionParser(SectionParserBase, ABC):
    """Base class for section parsers extracting textual blocks."""


__all__ = ["TextBlockSectionParser"]
