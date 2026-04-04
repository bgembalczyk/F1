from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.options import ScraperOptions

if TYPE_CHECKING:
    from collections.abc import Iterable

    from scrapers.base.parsers.soup import SoupParser

ParserInputT = TypeVar("ParserInputT")


@dataclass(frozen=True)
class InfoboxExtractionResult:
    """Wspólny kontrakt wyniku ekstrakcji infoboxów."""

    records: list[dict[str, Any]]

    @property
    def primary_record(self) -> dict[str, Any]:
        return self.records[0] if self.records else {}


class InfoboxExtractor(Protocol, Generic[ParserInputT]):
    """Strategia ekstrakcji infoboxów dla konkretnej domeny."""

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[ParserInputT]: ...

    def build_parser(
        self,
        *,
        options: ScraperOptions,
        url: str,
    ) -> SoupParser: ...

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult: ...


class InfoboxExtractionService(Protocol):
    """Wspólne API wymagane przez scrapery domenowe."""

    def extract(
        self,
        soup: BeautifulSoup,
        *,
        url: str = "",
    ) -> InfoboxExtractionResult: ...


class BaseInfoboxExtractionService(ABC, Generic[ParserInputT]):
    """Template method dla usług ekstrakcji infoboxów.

    Podklasy lub wstrzyknięte strategie definiują:
    - jak znaleźć infobox / infoboksy,
    - jak zbudować parser dla pojedynczego requestu,
    - jak znormalizować wynik do wspólnego kontraktu.
    """

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
            parsed_records.extend(self._coerce_records(parser.parse(infobox)))

        return self.normalize_result(parsed_records)

    @abstractmethod
    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[ParserInputT]:
        """Zwróć wszystkie fragmenty, które parser ma przetworzyć."""

    @abstractmethod
    def build_parser(self, *, url: str) -> SoupParser:
        """Zbuduj parser dopasowany do bieżącego requestu."""

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult:
        return InfoboxExtractionResult(records=parsed_records)

    @staticmethod
    def _coerce_records(raw_result: Any) -> list[dict[str, Any]]:
        if raw_result is None:
            return []
        if isinstance(raw_result, dict):
            return [raw_result]
        if isinstance(raw_result, list):
            return [record for record in raw_result if isinstance(record, dict)]
        msg = f"Unsupported infobox parser result: {type(raw_result)!r}"
        raise TypeError(msg)


class StrategyInfoboxExtractionService(BaseInfoboxExtractionService[ParserInputT]):
    """Adapter wykorzystujący strategię `InfoboxExtractor`."""

    def __init__(
        self,
        *,
        extractor: InfoboxExtractor[ParserInputT],
        options: ScraperOptions | None = None,
    ) -> None:
        super().__init__(options=options)
        self._extractor = extractor

    def find_infoboxes(self, soup: BeautifulSoup) -> Iterable[ParserInputT]:
        return self._extractor.find_infoboxes(soup)

    def build_parser(self, *, url: str) -> SoupParser:
        return self._extractor.build_parser(options=self._options, url=url)

    def normalize_result(
        self,
        parsed_records: list[dict[str, Any]],
    ) -> InfoboxExtractionResult:
        return self._extractor.normalize_result(parsed_records)


class FirstInfoboxTableExtractor:
    """Helper strategii zwracający pierwszy HTML-owy infobox tabelaryczny."""

    @staticmethod
    def find_infoboxes(soup: BeautifulSoup) -> list[Tag]:
        table = soup.find("table", class_="infobox")
        return [table] if isinstance(table, Tag) else []


class AllInfoboxTablesExtractor:
    """Helper strategii zwracający wszystkie HTML-owe tabele infobox."""

    @staticmethod
    def find_infoboxes(soup: BeautifulSoup) -> list[Tag]:
        return [
            table
            for table in soup.find_all("table", class_="infobox")
            if isinstance(table, Tag)
        ]
