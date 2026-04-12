from __future__ import annotations

from abc import ABC

from scrapers.parsers.contracts.wiki_elements import WikiSectionParserABC as SectionParserABC


class SeasonSectionParserABC(SectionParserABC, ABC):
    """Bazowy kontrakt parsera sekcji sezonowych."""




__all__ = ["SeasonSectionParserABC"]
