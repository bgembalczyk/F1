from pathlib import Path
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.list import ListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.sponsor import SponsorColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.headers import normalize_header
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline


class F1SponsorshipLiveriesScraper(F1Scraper):
    """
    Scraper tabel sponsorskich malowań F1:
    https://en.wikipedia.org/wiki/Formula_One_sponsorship_liveries

    Każda sekcja to jeden zespół, a w sekcji znajduje się tabela z kolumnami
    (opcjonalnymi) dotyczącymi sezonu i zmian malowania.
    """

    url = "https://en.wikipedia.org/wiki/Formula_One_sponsorship_liveries"
    _SKIP = object()
    _season_headers = {
        "year",
        "years",
        "season",
        "seasons",
    }
    _sponsor_keys = {
        "main_sponsors",
        "additional_major_sponsors",
        "livery_sponsors",
    }

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        options = init_scraper_options(options, include_urls=True)
        options.with_fetcher()
        super().__init__(options=options)

    def _build_pipeline(self) -> TablePipeline:
        config = ScraperConfig(
            url=self.url,
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
        )
        return TablePipeline(
            config=config,
            include_urls=self.include_urls,
            skip_sentinel=self._SKIP,
        )

    def _parse_section_table(
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
                records.extend(self._split_record_by_season(record))
        return records

    @staticmethod
    def _extract_year_params(params: list[str]) -> set[int]:
        years: set[int] = set()
        for param in params:
            for match in re.findall(r"\b\d{4}\b", str(param)):
                years.add(int(match))
        return years

    def _filter_sponsors_for_year(self, sponsors: Any, year: int) -> Any:
        if not isinstance(sponsors, list):
            return sponsors
        filtered: list[Any] = []
        for item in sponsors:
            if isinstance(item, dict):
                params = item.get("params") or []
                year_params = self._extract_year_params(params)
                if not year_params or year in year_params:
                    filtered.append(item)
                continue
            filtered.append(item)
        return filtered

    def _split_record_by_season(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        seasons = record.get("season")
        if not isinstance(seasons, list) or len(seasons) <= 1:
            return [record]

        season_entries = [
            season
            for season in seasons
            if isinstance(season, dict) and isinstance(season.get("year"), int)
        ]
        if len(season_entries) <= 1:
            return [record]

        split_records: list[Dict[str, Any]] = []
        for season_entry in season_entries:
            year = season_entry["year"]
            new_record = {**record, "season": [season_entry]}
            for key in self._sponsor_keys:
                if key in record:
                    new_record[key] = self._filter_sponsors_for_year(
                        record[key], year
                    )
            split_records.append(new_record)
        return split_records

    @staticmethod
    def _team_name_from_heading(heading: Tag, headline: Tag) -> str:
        if headline:
            return headline.get_text(" ", strip=True)
        headline_span = heading.find(class_="mw-headline")
        if headline_span:
            return headline_span.get_text(" ", strip=True)
        return heading.get_text(" ", strip=True)

    @staticmethod
    def _is_section_start(element: Tag, *, current_heading: Tag, current_headline: Tag) -> bool:
        if element is current_heading or element is current_headline:
            return False
        if "mw-headline" in (element.get("class") or []):
            return True
        if "mw-heading" in (element.get("class") or []):
            return True
        return element.name in {"h2", "h3", "h4", "h5", "h6"} and element.get("id")

    @staticmethod
    def _section_has_table(heading: Tag, headline: Tag) -> bool:
        return any(
            element.name == "table" and "wikitable" in (element.get("class") or [])
            for element in F1SponsorshipLiveriesScraper._iter_section_elements(
                heading, headline
            )
        )

    @staticmethod
    def _iter_section_elements(heading: Tag, headline: Tag) -> List[Tag]:
        elements: List[Tag] = []
        for element in heading.next_elements:
            if not isinstance(element, Tag):
                continue
            if F1SponsorshipLiveriesScraper._is_section_start(
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
            if element.name != "table" or "wikitable" not in (element.get("class") or []):
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

    def _parse_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
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
                        "liveries": self._parse_section_table(
                            soup,
                            section_id=section_id,
                            team=team,
                        ),
                    }
                )
            except RuntimeError:
                continue

        return records

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return self._parse_sections(soup)


if __name__ == "__main__":
    run_and_export(
        F1SponsorshipLiveriesScraper,
        "sponsorship_liveries/f1_sponsorship_liveries.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
