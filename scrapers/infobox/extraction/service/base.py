from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import Iterable

from bs4 import BeautifulSoup

from scrapers.base.infobox.extraction.result import InfoboxExtractionResult
from scrapers.base.infobox.extraction.result import ParserInputT
from scrapers.base.options import ScraperOptions
from scrapers.base.parsers.soup import SoupParser


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
