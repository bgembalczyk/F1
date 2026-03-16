from __future__ import annotations

from typing import Any
from typing import Protocol

from bs4 import BeautifulSoup


class ConstructorInfoboxExtractionServiceProtocol(Protocol):
    def extract(self, soup: BeautifulSoup) -> list[dict[str, Any]]: ...


class ConstructorSectionExtractionServiceProtocol(Protocol):
    def extract(self, soup: BeautifulSoup) -> list[dict[str, object]]: ...


class ConstructorRecordAssemblerProtocol(Protocol):
    def assemble(
        self,
        *,
        url: str,
        infoboxes: list[dict[str, Any]],
        tables: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> dict[str, Any]: ...
