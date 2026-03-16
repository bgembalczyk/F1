from __future__ import annotations

from typing import Any
from typing import Protocol

from bs4 import BeautifulSoup


class DriverInfoboxExtractionServiceProtocol(Protocol):
    def extract(self, soup: BeautifulSoup, *, url: str) -> dict[str, Any]: ...


class DriverSectionExtractionServiceProtocol(Protocol):
    def extract(self, soup: BeautifulSoup) -> list[dict[str, Any]]: ...


class DriverRecordAssemblerProtocol(Protocol):
    def assemble(
        self,
        *,
        url: str,
        infobox: dict[str, Any],
        career_results: list[dict[str, Any]],
    ) -> dict[str, Any]: ...
