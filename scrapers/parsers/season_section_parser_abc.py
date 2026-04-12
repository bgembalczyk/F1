from __future__ import annotations

from abc import ABC

from scrapers.parsers.base_family import SectionParserABC


class SeasonSectionParserABC(SectionParserABC, ABC):
    """Bazowy kontrakt parsera sekcji sezonowych."""




__all__ = ["SeasonSectionParserABC"]
