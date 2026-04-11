from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.columns.types.position import PositionColumn
from scrapers.config_table import TableScraperConfig
from scrapers.extractors.table import TableExtractor
from scrapers.options import ScraperOptions
from scrapers.scraper_table import F1TableScraper


class F1StandingsTableParser:
    """Parser tabel klasyfikacji (standings) Formuły 1.

    Parsuje tabelę klasyfikacji z podanego elementu HTML (``element``),
    stosując logikę obsługi remisów (TIED): jeżeli w kolumnie pozycji
    pojawia się wartość ``PositionColumn.TIED``, zastępuje ją poprzednią
    zapamiętaną pozycją.

    Dziedziczy po ``TableParser`` — jest wyłącznie parserem (nie pobiera
    HTML samodzielnie), zgodnie z hierarchią WikiElementParserów.
    """

    def __init__(self, *, position_key: str = "pos") -> None:
        self.position_key = position_key

    def normalize_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        previous_position = None
        for row in rows:
            pos = row.get(self.position_key)
            if pos is PositionColumn.TIED:
                row[self.position_key] = previous_position
            elif pos is not None:
                previous_position = pos
        return rows

    def parse(
        self,
        element: Tag,
        *,
        options: ScraperOptions,
        config: TableScraperConfig,
    ) -> list[dict[str, Any]]:
        extractor = TableExtractor(
            config=config,
            include_urls=options.include_urls,
            normalize_empty_values=options.normalize_empty_values,
        )
        rows = extractor.extract(element)
        return self.normalize_rows(rows)


class F1StandingsScraper(F1TableScraper):
    """Pełny scraper standings z pipeline fetch/parse."""

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: TableScraperConfig | None = None,
        position_key: str = "pos",
    ) -> None:
        super().__init__(options=options, config=config)
        self._table_parser = F1StandingsTableParser(position_key=position_key)

    def _parse_soup(self, soup: BeautifulSoup) -> list[Any]:
        rows = super()._parse_soup(soup)
        return self._table_parser.normalize_rows(rows)
