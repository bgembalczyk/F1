from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.headers import normalize_header
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.sponsorship_liveries.columns.colour import ColourListColumn
from scrapers.sponsorship_liveries.columns.seasons import SponsorshipSeasonsColumn
from scrapers.sponsorship_liveries.columns.sponsor import SponsorColumn
from scrapers.sponsorship_liveries.helpers.constants import season_headers
from scrapers.sponsorship_liveries.parsers.splitters.broader_scope import (
    BroaderScopeSplitter,
)
from scrapers.sponsorship_liveries.parsers.splitters.record.facade import (
    SponsorshipRecordSplitter,
)
from scrapers.wiki.parsers.elements.table import TableParser

if TYPE_CHECKING:
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class SponsorshipTableParser(TableParser):
    @staticmethod
    def build_schema(seasons_col_factory: Any) -> TableSchemaDSL:
        return TableSchemaDSL(
            columns=[
                *SponsorshipTableParser._season_column_specs(seasons_col_factory),
                *SponsorshipTableParser._driver_column_specs(),
                *SponsorshipTableParser._colour_column_specs(),
                *SponsorshipTableParser._sponsor_column_specs(),
                *SponsorshipTableParser._text_column_specs(),
            ],
        )

    @staticmethod
    def _season_column_specs(seasons_col_factory: Any) -> list[Any]:
        return [
            column("Year", "season", seasons_col_factory()),
            column("Years", "season", seasons_col_factory()),
            column("Season", "season", seasons_col_factory()),
            column("Seasons", "season", seasons_col_factory()),
            column("Year(s)", "season", seasons_col_factory()),
        ]

    @staticmethod
    def _driver_column_specs() -> list[Any]:
        return [column("Driver(s)", "drivers", DriverListColumn())]

    @staticmethod
    def _colour_column_specs() -> list[Any]:
        return [
            column(
                "Main colour(s)",
                normalize_header("Main colour(s)"),
                ColourListColumn(),
            ),
            column(
                "Additional colour(s)",
                normalize_header("Additional colour(s)"),
                ColourListColumn(),
            ),
        ]

    @staticmethod
    def _sponsor_column_specs() -> list[Any]:
        return [
            column(
                "Additional major sponsor(s)",
                normalize_header("Additional major sponsor(s)"),
                SponsorColumn(),
            ),
            column(
                "Livery sponsor(s)",
                normalize_header("Livery sponsor(s)"),
                SponsorColumn(),
            ),
            column(
                "Main sponsor(s)",
                normalize_header("Main sponsor(s)"),
                SponsorColumn(),
            ),
            column(
                "Livery principal sponsor(s)",
                "livery_principal_sponsors",
                SponsorColumn(),
            ),
        ]

    @staticmethod
    def _text_column_specs() -> list[Any]:
        return [
            column("Notes", normalize_header("Notes"), TextColumn()),
            column(
                "Non-tobacco liveries",
                normalize_header("Non-tobacco liveries"),
                TextColumn(),
            ),
            column(
                "Special liveries",
                normalize_header("Special liveries"),
                TextColumn(),
            ),
            column(
                "Non-tobacco/alcohol livery changes",
                normalize_header("Non-tobacco/alcohol livery changes"),
                TextColumn(),
            ),
            column(
                "Other Informations (including non-tobacco/alcohol race changes)",
                normalize_header(
                    "Other Informations (including non-tobacco/alcohol race changes)",
                ),
                TextColumn(),
            ),
            column(
                "Other information",
                normalize_header("Other information"),
                TextColumn(),
            ),
            column(
                "Non Tobacco/Alcohol changes(s)",
                normalize_header("Non Tobacco/Alcohol changes(s)"),
                TextColumn(),
            ),
            column(
                "Additional major sponsor(s) / Notes",
                normalize_header("Additional major sponsor(s) / Notes"),
                TextColumn(),
            ),
            column(
                "Location-specific livery changes (2011-present)",
                normalize_header("Location-specific livery changes (2011-present)"),
                TextColumn(),
            ),
            column(
                "Other Changes",
                normalize_header("Other Changes"),
                TextColumn(),
            ),
        ]


class SponsorshipSectionParser:
    def __init__(
        self,
        *,
        url: str,
        include_urls: bool,
        normalize_empty_values: bool,
        splitter: SponsorshipRecordSplitter,
        classifier: Optional["ParenClassifier"] = None,
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

        config = ScraperConfig(
            url=self._url,
            schema=SponsorshipTableParser.build_schema(_seasons_col),
            record_factory=RECORD_FACTORIES.mapping(),
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
