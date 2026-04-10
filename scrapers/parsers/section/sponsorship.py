from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

from bs4 import BeautifulSoup
from bs4 import Tag

from models.records.factories.mapping import MappingRecordFactory
from scrapers.columns.types.sponsorship_seasons import SponsorshipSeasonsColumn
from scrapers.configs.public import TableConfig
from scrapers.headers_table import normalize_header
from scrapers.helpers.constants import season_headers
from scrapers.helpers.text import clean_wiki_text
from scrapers.paren_classifier import ParenClassifier
from scrapers.parser_table import HtmlTableParser
from scrapers.parsers.liveries.sponsorship.splitters.broader_scope import BroaderScopeSplitter
from scrapers.parsers.liveries.sponsorship.splitters.record.facade import SponsorshipRecordSplitter
from scrapers.parsers.table.sponsorship import SponsorshipTableParser
from scrapers.pipeline_table import TablePipeline


class SponsorshipSectionParser:
    def __init__(
        self,
        *,
        url: str,
        include_urls: bool,
        normalize_empty_values: bool,
        splitter: SponsorshipRecordSplitter,
        classifier: Optional[ParenClassifier] = None,
    ):
        self._url = url
        self._include_urls = include_urls
        self._normalize_empty_values = normalize_empty_values
        self._splitter = splitter
        self._classifier = classifier

    def _build_pipeline(
        self,
        *,
        team_name: str | None = None,
        table_headers: list[str] | None = None,
    ) -> TablePipeline:
        def _seasons_col() -> SponsorshipSeasonsColumn:
            return SponsorshipSeasonsColumn(
                team_name=team_name,
                classifier=self._classifier,
                table_headers=table_headers,
            )

        config = TableConfig(
            url=self._url,
            schema=SponsorshipTableParser.build_schema(_seasons_col),
            record_factory=MappingRecordFactory(),
        )
        return TablePipeline(
            config=config,
            include_urls=self._include_urls,
            normalize_empty_values=self._normalize_empty_values,
        )

    def parse_section_table(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
        team: str,
    ) -> list[dict[str, Any]]:
        parser = HtmlTableParser(table_css_class="wikitable")
        table = self._find_section_table(soup, section_id=section_id)
        rows = parser.parse_table(table)
        table_headers = list(rows[0].headers) if rows else []
        pipeline = self._build_pipeline(
            team_name=team,
            table_headers=table_headers,
        )
        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(rows):
            record = pipeline.parse_cells(
                row.headers,
                row.cells,
                row_index=row_index,
            )
            if record:
                records.extend(self._splitter.split_record_by_season(record))
        return self._split_broader_records_by_scope(records)

    @staticmethod
    def _split_broader_records_by_scope(
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        season_scoped = SponsorshipSectionParser._season_scoped_records(records)
        if not season_scoped:
            return records
        return BroaderScopeSplitter(records, season_scoped).split()

    @staticmethod
    def _season_scoped_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [r for r in records if r.get("_season_scoped_gp")]

    @staticmethod
    def _team_name_from_heading(heading: Tag, headline: Tag) -> str:
        if headline:
            return headline.get_text(" ", strip=True)
        headline_span = heading.find(class_="mw-headline")
        if headline_span:
            return headline_span.get_text(" ", strip=True)
        return heading.get_text(" ", strip=True)

    @staticmethod
    def team_name_from_heading(heading: Tag, headline: Tag) -> str:
        return SponsorshipSectionParser._team_name_from_heading(heading, headline)

    @staticmethod
    def _is_section_start(
        element: Tag,
        *,
        current_heading: Tag,
        current_headline: Tag,
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
    def section_has_table(cls, heading: Tag, headline: Tag) -> bool:
        return cls._section_has_table(heading, headline)

    @classmethod
    def _iter_section_elements(cls, heading: Tag, headline: Tag) -> list[Tag]:
        elements: list[Tag] = []
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
            msg = f"Nie znaleziono sekcji o id={section_id!r}"
            raise TypeError(msg)
        heading = headline.parent
        if not isinstance(heading, Tag):
            msg = f"Nie znaleziono nagłówka sekcji {section_id!r}"
            raise TypeError(msg)

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
            if any(h in season_headers for h in headers):
                return element

        msg = f"Nie znaleziono tabeli w sekcji {section_id!r}"
        raise RuntimeError(msg)

    def parse_sections(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        seen_sections: set[str] = set()
        for heading, headline in self._collect_section_headings(soup):
            section_id = self._section_id_if_new(headline, seen_sections)
            if not section_id:
                continue
            section_record = self._parse_heading(soup, heading, headline, section_id)
            if section_record:
                records.append(section_record)
        return records

    def _parse_heading(
        self,
        soup: BeautifulSoup,
        heading: Tag,
        headline: Tag,
        section_id: str,
    ) -> dict[str, Any] | None:
        return self._parse_section_heading_record(
            soup,
            heading,
            headline,
            section_id,
        )

    @staticmethod
    def _section_id_if_new(headline: Tag, seen_sections: set[str]) -> str | None:
        section_id = headline.get("id")
        if not section_id or section_id in seen_sections:
            return None
        seen_sections.add(section_id)
        return section_id

    @staticmethod
    def section_id_if_new(headline: Tag, seen_sections: set[str]) -> str | None:
        return SponsorshipSectionParser._section_id_if_new(headline, seen_sections)

    def _parse_section_heading_record(
        self,
        soup: BeautifulSoup,
        heading: Tag,
        headline: Tag,
        section_id: str,
    ) -> dict[str, Any] | None:
        team = self._team_name_from_heading(heading, headline)
        if not self._section_has_table(heading, headline):
            return None
        return self._parse_single_section_record(soup, section_id, team)

    @staticmethod
    def _collect_section_headings(soup: BeautifulSoup) -> list[tuple[Tag, Tag]]:
        headings: list[tuple[Tag, Tag]] = []
        for headline in soup.select(".mw-headline"):
            heading = headline.parent
            if isinstance(heading, Tag):
                headings.append((heading, headline))
        for heading in soup.select(".mw-heading"):
            headline = heading.find(["h2", "h3", "h4", "h5", "h6"], id=True)
            if headline:
                headings.append((heading, headline))
        if headings:
            return headings
        for headline in soup.select("h2[id], h3[id], h4[id], h5[id], h6[id]"):
            heading = headline.parent
            if isinstance(heading, Tag):
                headings.append((heading, headline))
        return headings

    @staticmethod
    def collect_section_headings(soup: BeautifulSoup) -> list[tuple[Tag, Tag]]:
        return SponsorshipSectionParser._collect_section_headings(soup)

    def _parse_single_section_record(
        self,
        soup: BeautifulSoup,
        section_id: str,
        team: str,
    ) -> dict[str, Any] | None:
        try:
            liveries = self.parse_section_table(soup, section_id=section_id, team=team)
        except RuntimeError:
            return None
        return {"team": team, "liveries": liveries}


__all__ = [
    "SponsorshipSectionParser",
]
