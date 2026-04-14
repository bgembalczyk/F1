from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from typing import Any
from typing import Generic

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.result import InfoboxExtractionResult
from scrapers.infobox.extraction.result import ParserInputT
from scrapers.options import ScraperOptions
from scrapers.parsers.soup import SoupParser


class BaseInfoboxOrchestrator(ABC, Generic[ParserInputT]):
    """Template-method orchestrator for infobox extraction domains."""

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        self._options = options or ScraperOptions()

    def extract(
        self,
        soup: BeautifulSoup,
        *,
        url: str = "",
    ) -> InfoboxExtractionResult:
        parser = self.build_parser(url=url)
        parsed_records: list[dict[str, Any]] = []

        for infobox in self.find_infoboxes(soup):
            parsed_records.extend(self.coerce_records(parser.parse(infobox)))

        return self.normalize_result(parsed_records)

    @abstractmethod
    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[ParserInputT]:
        """Return all parsed fragments for the current request."""

    @abstractmethod
    def build_parser(self, *, url: str) -> SoupParser:
        """Build parser fitted to current request metadata."""

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult:
        return InfoboxExtractionResult(records=parsed_records)

    @staticmethod
    def coerce_records(raw_result: Any) -> list[dict[str, Any]]:
        if raw_result is None:
            return []
        if isinstance(raw_result, dict):
            return [raw_result]
        if isinstance(raw_result, list):
            return [record for record in raw_result if isinstance(record, dict)]
        msg = f"Unsupported infobox parser result: {type(raw_result)!r}"
        raise TypeError(msg)
