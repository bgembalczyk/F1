from __future__ import annotations

from scrapers.parsers.roles import SectionParser as SectionParser

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
