from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.runner import RunConfig, run_and_export
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.list import ListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
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

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        options = init_scraper_options(options, include_urls=True)
        options.with_fetcher()
        super().__init__(options=options)

    def _build_pipeline(self) -> TablePipeline:
        config = ScraperConfig(
            url=self.url,
            expected_headers=["Year"],
            column_map={
                "Year": "season",
                "Driver(s)": "drivers",
            },
            columns={
                "season": SeasonsColumn(),
                "drivers": DriverListColumn(),
                "Main colour(s)": ListColumn(),
                "Additional colour(s)": ListColumn(),
                "Additional major sponsor(s)": ListColumn(),
                "Livery sponsor(s)": ListColumn(),
                "Main sponsor(s)": ListColumn(),
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
        )

    def _parse_section_table(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
        team: str,
    ) -> List[Dict[str, Any]]:
        pipeline = self._build_pipeline()
        parser = HtmlTableParser(
            section_id=section_id,
            expected_headers=pipeline.expected_headers,
            table_css_class=pipeline.table_css_class,
        )
        records: List[Dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse(soup)):
            record = pipeline.parse_cells(
                row.headers,
                row.cells,
                row_index=row_index,
            )
            if record:
                record["team"] = team
                records.append(record)
        return records

    @staticmethod
    def _team_name_from_heading(heading: Tag) -> str:
        headline = heading.find(class_="mw-headline")
        if headline:
            return headline.get_text(" ", strip=True)
        return heading.get_text(" ", strip=True)

    @staticmethod
    def _section_has_table(heading: Tag, headline: Tag) -> bool:
        for element in heading.next_elements:
            if not isinstance(element, Tag):
                continue
            if element is headline:
                continue
            if "mw-headline" in (element.get("class") or []):
                return False
            if element.name == "table" and "wikitable" in (element.get("class") or []):
                return True
        return False

    def _parse_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        headings = soup.select(".mw-headline")
        for headline in headings:
            section_id = headline.get("id")
            if not section_id:
                continue

            heading = headline.parent
            if not isinstance(heading, Tag):
                continue

            team = self._team_name_from_heading(heading)
            if not self._section_has_table(heading, headline):
                continue

            try:
                records.extend(
                    self._parse_section_table(
                        soup,
                        section_id=section_id,
                        team=team,
                    )
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
        "sponsorship_liveries/f1_sponsorship_liveries.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
