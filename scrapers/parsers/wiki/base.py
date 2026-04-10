from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from bs4 import Tag

TWikiParsed = TypeVar("TWikiParsed")


class WikiParser(ABC, Generic[TWikiParsed]):
    """Bazowa klasa dla wszystkich parserów HTML Wikipedii.

    Parser przetwarza konkretny fragment HTML (Tag) i zwraca
    wyekstrahowane dane w postaci słownika.
    """

    @abstractmethod
    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> TWikiParsed:
        """Parsuje przekazany element HTML.

        Args:
            element: Element BeautifulSoup do sparsowania.

        Returns:
            Wyekstrahowane dane (format zależy od konkretnego parsera).
        """
