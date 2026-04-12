from __future__ import annotations

from abc import ABC

from scrapers.parsers.wiki_section_parser_abc import WikiSectionParserABC


class SeasonSectionParserABC(WikiSectionParserABC, ABC):
    """Bazowy kontrakt parsera sekcji sezonowych."""




__all__ = ["SeasonSectionParserABC"]
