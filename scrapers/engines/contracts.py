from __future__ import annotations

from typing import Any
from typing import Protocol

from bs4 import BeautifulSoup


class EngineInfoboxParserProtocol(Protocol):
    def parse_element(self, element: Any) -> dict[str, Any]: ...


class EngineArticleTablesParserProtocol(Protocol):
    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]: ...
