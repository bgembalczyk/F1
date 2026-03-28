from typing import Any

from bs4 import Tag

from scrapers.base.extractors.table import TableExtractor
from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.config import TableScraperConfig
from scrapers.wiki.parsers.elements.table import TableParser


class F1StandingsScraper(TableParser):
    """Parser tabel klasyfikacji (standings) Formuły 1.

    Parsuje tabelę klasyfikacji z podanego elementu HTML (``element``),
    stosując logikę obsługi remisów (TIED): jeżeli w kolumnie pozycji
    pojawia się wartość ``PositionColumn.TIED``, zastępuje ją poprzednią
    zapamiętaną pozycją.

    Dziedziczy po ``TableParser`` — jest wyłącznie parserem (nie pobiera
    HTML samodzielnie), zgodnie z hierarchią WikiElementParserów.
    """

    def __init__(
        self,
        *,
        options: ScraperOptions,
        config: TableScraperConfig,
        position_key: str = "pos",
    ) -> None:
        self.position_key = position_key
        self._extractor = TableExtractor(
            config=config,
            include_urls=options.include_urls,
            normalize_empty_values=options.normalize_empty_values,
        )

    def parse(self, element: Tag) -> list[dict[str, Any]]:
        rows = self._extractor.extract(element)
        previous_position = None
        for row in rows:
            pos = row.get(self.position_key)
            if pos is PositionColumn.TIED:
                row[self.position_key] = previous_position
            elif pos is not None:
                previous_position = pos
        return rows
