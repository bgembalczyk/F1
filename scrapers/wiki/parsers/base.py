from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag

from scrapers.wiki.parsers.context import WikiParserContext


class WikiParser(ABC):
    """Bazowa klasa dla wszystkich parserów HTML Wikipedii.

    Parser przetwarza konkretny fragment HTML (Tag) i zwraca
    wyekstrahowane dane w postaci słownika.
    """

    @abstractmethod
    def parse(self, element: Tag, context: WikiParserContext | None = None) -> Any:
        """Parsuje przekazany element HTML.

        Args:
            element: Element BeautifulSoup do sparsowania.
            context: Opcjonalny kontekst parsowania Wikipedii.

        Returns:
            Wyekstrahowane dane (format zależy od konkretnego parsera).
        """
