from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_metadata
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.lap_record import is_lap_record_table
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.base.options import ScraperOptions


class CircuitLapRecordsSectionParser:
    def __init__(self, *, options: ScraperOptions, url: str) -> None:
        self._options = options
        self._url = url
        self._tables = ArticleTablesParser(include_source_table=True)

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        lap_scraper = LapRecordsTableScraper(options=self._options)
        lap_scraper.url = self._url
        all_records: list[dict[str, object]] = []
        for table_data in self._tables.parse(section_fragment):
            table = table_data.get("_table")
            if table is None:
                continue
            headers = table_data.get("headers") or []
            if not is_lap_record_table(headers, lap_scraper):
                continue
            layout = detect_layout_name(table, headers)
            all_records.extend(collect_lap_records(table, headers, layout, lap_scraper))

        return SectionParseResult(
            section_id="lap_records",
            section_label="Lap records",
            records=all_records,
            metadata=build_section_metadata(parser=self.__class__.__name__, source="wikipedia"),
        )
