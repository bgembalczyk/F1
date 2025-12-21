from __future__ import annotations

from typing import Any, Protocol

from bs4 import BeautifulSoup


class SoupParser(Protocol):
    def parse(self, soup: BeautifulSoup) -> Any:
        """Zamienia soup na docelową strukturę danych."""
