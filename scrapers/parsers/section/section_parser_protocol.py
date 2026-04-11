from __future__ import annotations

from scrapers.parsers.roles import SectionParser as SectionParserProtocol

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
