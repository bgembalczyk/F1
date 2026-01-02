from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.helpers.html_utils import clean_wiki_text
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper
from scrapers.circuits.helpers.article_validation import is_circuit_like_article
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.lap_record import is_lap_record_table
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.circuits.infobox.scraper import F1CircuitInfoboxScraper


class F1SingleCircuitScraper(WikipediaSectionByIdMixin, F1Scraper):
    """
    Scraper pojedynczego toru – pobiera infobox i wszystkie tabele z artykułu Wikipedii.

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
        options.with_fetcher()

        super().__init__(options=options)
        self.policy = options.to_http_policy()
        self.timeout = self.policy.timeout
        self.url: str = ""
        self._original_url: Optional[str] = None
        self._section_fragment: Optional[str] = None

    def fetch_html(self, url: str) -> str:
        return self.source_adapter.get(url, timeout=self.timeout)

    def _select_section(
        self,
        soup: BeautifulSoup,
        fragment: Optional[str],
    ) -> BeautifulSoup:
        if not fragment:
            return soup

        section = self._extract_section_by_id(soup, fragment)
        return section or soup

    def _parse_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        return {
            "infobox": self._scrape_infobox(soup),
            "tables": self._scrape_tables(soup),
        }

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
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
            }
        ]

    def _scrape_infobox(self, soup: BeautifulSoup) -> Dict[str, Any]:
        infobox_scraper = F1CircuitInfoboxScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                policy=self.policy,
            ),
        )
        records = infobox_scraper.parse(soup)
        return records[0] if records else {}

    def _scrape_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        lap_scraper = LapRecordsTableScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                policy=self.policy,
            ),
        )
        lap_scraper.url = self.url  # żeby _full_url działało poprawnie
        all_records: List[Dict[str, Any]] = []

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
                collect_lap_records(table, headers, base_layout, lap_scraper)
            )

        layouts: Dict[str, List[Dict[str, Any]]] = {}
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
