from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from scrapers.parsers.contracts.wiki_elements import WikiSectionParserABC

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.section.parse_results import SectionParseResult



class BaseSectionParser(WikiSectionParserABC):
    """Canonical runtime base class for section parsers."""

    @abstractmethod
    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        """Public entrypoint parsera sekcji."""

    def _parse_group(self, *args: object, **kwargs: object) -> object:
        """Wewnętrzny helper dla parserów opartych o grupowanie elementów."""

        _ = args
        _ = kwargs
        raise NotImplementedError

    def _parse_children(self, *args: object, **kwargs: object) -> object:
        """Wewnętrzny helper dla parserów opartych o iterację po dzieciach."""

        _ = args
        _ = kwargs
        raise NotImplementedError


__all__ = ["BaseSectionParser"]
