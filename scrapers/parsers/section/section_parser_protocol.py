from __future__ import annotations

import warnings

from scrapers.parsers.roles import SectionParserABC
from scrapers.parsers.section.base import BaseSectionParser


class LegacySectionParser(BaseSectionParser):
    """Deprecated runtime alias kept for safe migration."""

    def __init_subclass__(cls, **kwargs):
        warnings.warn(
            "LegacySectionParser is deprecated; inherit from BaseSectionParser instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init_subclass__(**kwargs)


__all__ = ["SectionParserABC", "LegacySectionParser"]
