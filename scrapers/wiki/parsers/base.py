from abc import ABC
from abc import abstractmethod
from typing import Any

from bs4 import Tag


class WikiParser(ABC):
    """Bazowa klasa dla wszystkich parserów HTML Wikipedii.

    Parser przetwarza konkretny fragment HTML (Tag) i zwraca
    wyekstrahowane dane w postaci słownika.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

    @abstractmethod
    def parse(self, element: Tag) -> Any:
        """Parsuje przekazany element HTML.

        Args:
            element: Element BeautifulSoup do sparsowania.

        Returns:
            Wyekstrahowane dane (format zależy od konkretnego parsera).
        """
