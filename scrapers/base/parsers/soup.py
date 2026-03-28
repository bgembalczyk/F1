from typing import Any
from typing import Protocol

from bs4 import BeautifulSoup


class SoupParser(Protocol):
    def parse(self, soup: BeautifulSoup) -> Any:
        """Zamienia soup na docelową strukturę danych."""
