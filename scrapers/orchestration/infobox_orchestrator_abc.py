from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.result import InfoboxExtractionResult


class InfoboxOrchestratorABC(ABC):
    """Common API required by domain scrapers."""

    @abstractmethod
    def extract(
        self,
        soup: BeautifulSoup,
        *,
        url: str = "",
    ) -> InfoboxExtractionResult: ...


__all__ = ["InfoboxOrchestratorABC"]
