from __future__ import annotations

from typing import Any

from bs4 import Tag

from scrapers.columns.types.position import PositionColumn
from scrapers.config_table import TableScraperConfig
from scrapers.extractors.table import TableExtractor
from scrapers.options import ScraperOptions
from scrapers.parsers.tag_parser_abc import HtmlTagParserABC


class F1StandingsTableParser(HtmlTagParserABC[list[dict[str, Any]]]):
    """Parser tabel klasyfikacji (standings) Formuły 1."""

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
        raw: Tag,
        *,
        options: ScraperOptions,
        config: TableScraperConfig,
    ) -> list[dict[str, Any]]:
        extractor = TableExtractor(
            config=config,
            include_urls=options.include_urls,
            normalize_empty_values=options.normalize_empty_values,
        )
        rows = extractor.extract(raw)
        return self.normalize_rows(rows)


__all__ = ["F1StandingsTableParser"]

