from typing import Protocol
from typing import TypeVar
from typing import runtime_checkable

from bs4 import BeautifulSoup

SoupParseResultT_co = TypeVar("SoupParseResultT_co", covariant=True)


@runtime_checkable
class SoupParser(Protocol[SoupParseResultT_co]):
    def parse(self, soup: BeautifulSoup) -> SoupParseResultT_co:
        """Zamienia soup na docelową strukturę danych."""
