from __future__ import annotations

from abc import ABC

from scrapers.parsers.roles import SectionStructureParserABC


class SeasonSectionParserABC(SectionStructureParserABC, ABC):
    """Bazowy kontrakt parsera sekcji sezonowych."""




__all__ = ["SeasonSectionParserABC"]
