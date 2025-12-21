from __future__ import annotations

from typing import Any, Dict, List, Protocol

from bs4 import BeautifulSoup


class SoupParser(Protocol):
    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Zamienia soup na listę rekordów."""
