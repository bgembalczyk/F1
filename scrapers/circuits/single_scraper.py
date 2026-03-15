from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.options import ScraperOptions
from scrapers.circuits.helpers.article_validation import is_circuit_like_article
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.lap_record import is_lap_record_table
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.circuits.infobox.scraper import F1CircuitInfoboxParser
from scrapers.wiki.scraper import WikiScraper


class F1SingleCircuitScraper(WikiScraper):
    """
    Scraper pojedynczego toru - pobiera infobox i wszystkie tabele z artykułu Wikipedii.

    Dodatkowe heurystyki:
    - jeżeli artykuł nie ma kategorii typu '... circuit / racetrack / speedway ...'
      → zwracamy None (nie zbieramy dodatkowych informacji),
    - jeżeli URL ma fragment (#Bugatti_Circuit) → szukamy infoboksa i tabel tylko
      wewnątrz tej sekcji.
    """

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        # Ten scraper zawsze potrzebuje URL-i (lap records, encje itd.)
        options = init_scraper_options(options, include_urls=True)

        # HtmlFetcher jest config-driven — jeśli nie ma fetchera w options,
        # tworzymy domyślny.
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)

        super().__init__(options=options)
        self.policy = self.http_policy
        self.url: str = ""
        self.debug_dir = options.debug_dir
        self._original_url: str | None = None
        self._section_fragment: str | None = None

    def _select_section(
        self,
        soup: BeautifulSoup,
        fragment: str | None,
    ) -> BeautifulSoup:
        if not fragment:
            return soup

        section = self.find_section(soup, fragment)
        return section.soup if section is not None else soup

    def _parse_details(self, soup: BeautifulSoup) -> dict[str, Any]:
        return {
            "infobox": self._scrape_infobox(soup),
            "tables": self._scrape_tables(soup),
        }

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if not is_circuit_like_article(soup):
            return []

        working_soup = self._select_section(soup, self._section_fragment)

        if self.parser is not None:
            return self.parser.parse(working_soup)

        parsed = self._parse_details(working_soup)
        if not parsed:
            return []

        return [
            {
                "url": self._original_url or self.url,
                **parsed,
            },
        ]

    def _scrape_infobox(self, soup: BeautifulSoup) -> dict[str, Any]:
        infobox_parser = F1CircuitInfoboxParser(
            options=ScraperOptions(
                include_urls=self.include_urls,
                debug_dir=self.debug_dir,
            ),
            url=self.url,
        )
        records = infobox_parser.parse(soup)
        return records[0] if records else {}

    def _scrape_tables(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        lap_scraper = LapRecordsTableScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                policy=self.policy,
                debug_dir=self.debug_dir,
            ),
        )
        lap_scraper.url = self.url  # żeby _full_url działało poprawnie
        all_records: list[dict[str, Any]] = []

        for table in soup.find_all("table", class_="wikitable"):
            header_row = table.find("tr")
            if not header_row:
                continue

            header_cells = header_row.find_all(["th", "td"])
            headers = [clean_wiki_text(c.get_text(strip=True)) for c in header_cells]

            if not is_lap_record_table(headers, lap_scraper):
                continue

            base_layout = detect_layout_name(table, headers)
            all_records.extend(
                collect_lap_records(table, headers, base_layout, lap_scraper),
            )

        layouts: dict[str, list[dict[str, Any]]] = {}
        for rec in all_records:
            layout_name = rec.get("layout")
            if not layout_name:
                continue

            rec_copy = dict(rec)
            rec_copy.pop("layout", None)
            layouts.setdefault(layout_name, []).append(rec_copy)

        return [
            {"layout": layout_name, "lap_records": recs}
            for layout_name, recs in layouts.items()
        ]
