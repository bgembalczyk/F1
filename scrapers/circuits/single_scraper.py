from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.circuits.helpers.article_validation import is_circuit_like_article
from scrapers.circuits.helpers.lap_record import collect_lap_records
from scrapers.circuits.helpers.lap_record import is_lap_record_table
from scrapers.circuits.helpers.layout import detect_layout_name
from scrapers.circuits.infobox.scraper import F1CircuitInfoboxParser
from scrapers.circuits.sections import circuit_section_entries
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser
from scrapers.wiki.scraper import WikiScraper
from scrapers.circuits.postprocess import CircuitSectionContractPostProcessor


class F1SingleCircuitScraper(SectionAdapter, WikipediaSectionByIdMixin, WikiScraper):
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

        options.post_processors.append(CircuitSectionContractPostProcessor())
        super().__init__(options=options)
        self.policy = self.http_policy
        self.url: str = ""
        self.debug_dir = options.debug_dir
        self._original_url: str | None = None
        self._section_fragment: str | None = None
        self.article_tables_parser = ArticleTablesParser(include_source_table=True)

    def _select_section(
        self,
        soup: BeautifulSoup,
        fragment: str | None,
    ) -> BeautifulSoup:
        if not fragment:
            return soup

        section = self.extract_section_by_id(soup, fragment, domain="circuits")
        return section or soup

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
                "sections": self.parse_section_dicts(
                    soup=working_soup,
                    domain="circuits",
                    entries=circuit_section_entries(
                        options=ScraperOptions(
                            include_urls=self.include_urls,
                            fetcher=self.fetcher,
                            policy=self.policy,
                            debug_dir=self.debug_dir,
                        ),
                        url=self.url,
                    ),
                ),
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

        for table_data in self.article_tables_parser.parse(soup):
            table = table_data.get("_table")
            if table is None:
                continue

            headers = table_data["headers"]
            table_type = table_data.get("table_type")
            if table_type != "lap_records" and not is_lap_record_table(
                headers, lap_scraper
            ):
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
