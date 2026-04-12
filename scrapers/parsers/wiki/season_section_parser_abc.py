from __future__ import annotations

from abc import ABC

from scrapers.parsers.contracts.wiki_elements import WikiSectionElementParserABC


class SeasonSectionParserABC(WikiSectionElementParserABC, ABC):
    """Bazowy kontrakt parsera sekcji sezonowych."""




__all__ = ["SeasonSectionParserABC"]
