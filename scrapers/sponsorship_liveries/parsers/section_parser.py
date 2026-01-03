from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.list import ListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.sponsor import SponsorColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.headers import normalize_header
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.sponsorship_liveries.parsers.record_splitter import (
    SponsorshipRecordSplitter,
)


class SponsorshipSectionParser:
    _SKIP = object()
    _season_headers = {
        "year",
        "years",
        "season",
        "seasons",
    }

    def __init__(
        self,
        *,
        include_urls: bool,
        normalize_empty_values: bool,
        splitter: SponsorshipRecordSplitter,
    ):
        self._include_urls = include_urls
        self._normalize_empty_values = normalize_empty_values
        self._splitter = splitter

    def _build_pipeline(self) -> TablePipeline:
        config = ScraperConfig(
            column_map={
                "Year": "season",
                "Years": "season",
                "Season": "season",
                "Seasons": "season",
                "Year(s)": "season",
                "Driver(s)": "drivers",
            },
            columns={
                "season": SeasonsColumn(),
                "drivers": DriverListColumn(),
                "Main colour(s)": ListColumn(),
                "Additional colour(s)": ListColumn(),
                "Additional major sponsor(s)": SponsorColumn(),
                "Livery sponsor(s)": SponsorColumn(),
                "Main sponsor(s)": SponsorColumn(),
                "Notes": TextColumn(),
                "Non-tobacco liveries": TextColumn(),
                "Special liveries": TextColumn(),
                "Non-tobacco/alcohol livery changes": TextColumn(),
                "Other Informations (including non-tobacco/alcohol race changes)": TextColumn(),
                "Other information": TextColumn(),
                "Non Tobacco/Alcohol changes(s)": TextColumn(),
                "Additional major sponsor(s) / Notes": TextColumn(),
                "Location-specific livery changes (2011–present)": TextColumn(),
                "Other Changes": TextColumn(),
            },
            record_factory=record_from_mapping,
        )
        return TablePipeline(
            config=config,
            include_urls=self._include_urls,
            skip_sentinel=self._SKIP,
            normalize_empty_values=self._normalize_empty_values,
        )

    def parse_section_table(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
        team: str,
    ) -> List[Dict[str, Any]]:
        pipeline = self._build_pipeline()
        parser = HtmlTableParser(table_css_class=pipeline.table_css_class)
        table = self._find_section_table(soup, section_id=section_id)
        records: List[Dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse_table(table)):
            record = pipeline.parse_cells(
                row.headers,
                row.cells,
                row_index=row_index,
            )
            if record:
                records.extend(self._splitter.split_record_by_season(record))
        return records

    @staticmethod
    def _team_name_from_heading(heading: Tag, headline: Tag) -> str:
        if headline:
            return headline.get_text(" ", strip=True)
        headline_span = heading.find(class_="mw-headline")
        if headline_span:
            return headline_span.get_text(" ", strip=True)
        return heading.get_text(" ", strip=True)

    @staticmethod
    def _is_section_start(
        element: Tag, *, current_heading: Tag, current_headline: Tag
    ) -> bool:
        if element is current_heading or element is current_headline:
            return False
        if "mw-headline" in (element.get("class") or []):
            return True
        if "mw-heading" in (element.get("class") or []):
            return True
        return element.name in {"h2", "h3", "h4", "h5", "h6"} and element.get("id")

    @classmethod
    def _section_has_table(cls, heading: Tag, headline: Tag) -> bool:
        return any(
            element.name == "table" and "wikitable" in (element.get("class") or [])
            for element in cls._iter_section_elements(heading, headline)
        )

    @classmethod
    def _iter_section_elements(cls, heading: Tag, headline: Tag) -> List[Tag]:
        elements: List[Tag] = []
        for element in heading.next_elements:
            if not isinstance(element, Tag):
                continue
            if cls._is_section_start(
                element,
                current_heading=heading,
                current_headline=headline,
            ):
                break
            elements.append(element)
        return elements

    def _find_section_table(self, soup: BeautifulSoup, *, section_id: str) -> Tag:
        headline = soup.find(id=section_id)
        if not isinstance(headline, Tag):
            raise RuntimeError(f"Nie znaleziono sekcji o id={section_id!r}")
        heading = headline.parent
        if not isinstance(heading, Tag):
            raise RuntimeError(f"Nie znaleziono nagłówka sekcji {section_id!r}")

        for element in self._iter_section_elements(heading, headline):
            if element.name != "table" or "wikitable" not in (
                element.get("class") or []
            ):
                continue
            header_row = element.find("tr")
            if not header_row:
                continue
            header_cells = header_row.find_all(["th", "td"])
            headers = [
                normalize_header(clean_wiki_text(c.get_text(" ", strip=True)))
                for c in header_cells
            ]
            if any(h in self._season_headers for h in headers):
                return element

        raise RuntimeError(f"Nie znaleziono tabeli w sekcji {section_id!r}")

    def parse_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        headings = []
        for headline in soup.select(".mw-headline"):
            heading = headline.parent
            if isinstance(heading, Tag):
                headings.append((heading, headline))
        for heading in soup.select(".mw-heading"):
            headline = heading.find(["h2", "h3", "h4", "h5", "h6"], id=True)
            if headline:
                headings.append((heading, headline))
        if not headings:
            for headline in soup.select("h2[id], h3[id], h4[id], h5[id], h6[id]"):
                heading = headline.parent
                if isinstance(heading, Tag):
                    headings.append((heading, headline))

        seen_sections = set()
        for heading, headline in headings:
            section_id = headline.get("id")
            if not section_id or section_id in seen_sections:
                continue
            seen_sections.add(section_id)

            team = self._team_name_from_heading(heading, headline)
            if not self._section_has_table(heading, headline):
                continue

            try:
                records.append(
                    {
                        "team": team,
                        "liveries": self.parse_section_table(
                            soup,
                            section_id=section_id,
                            team=team,
                        ),
                    }
                )
            except RuntimeError:
                continue

        return records
