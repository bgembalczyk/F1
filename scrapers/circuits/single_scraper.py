from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.tables.header import is_repeated_header_row
from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.helpers.html_utils import clean_wiki_text
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.scraper import F1Scraper
from scrapers.base.errors import ScraperError, ScraperParseError
from scrapers.circuits.infobox.scraper import F1CircuitInfoboxScraper

_LAP_RECORDS_CONTEXT: LapRecordsTableScraper | None = None

logger = logging.getLogger(__name__)


def _layout_from_spanning_header(
    cells: list[Tag],
    headers: list[str],
) -> Optional[str]:
    if len(cells) != 1 or cells[0].name != "th":
        return None

    th = cells[0]
    try:
        colspan = int(th.get("colspan", "1"))
    except ValueError:
        colspan = 1

    text = clean_wiki_text(th.get_text(strip=True))
    if not text:
        return None

    keywords = (
        "circuit",
        "layout",
        "course",
        "km",
        "mi",
        "present",
        "configuration",
    )

    if colspan >= len(headers) or any(kw in text.lower() for kw in keywords):
        return text

    return None


def is_lap_record_table(headers: list[str]) -> bool:
    lap_scraper = LapRecordsTableScraper()
    if lap_scraper.headers_match(headers):
        return True

    header_set = set(headers)
    return "Time" in header_set and (
        "Driver" in header_set or "Driver/Rider" in header_set
    )


def detect_layout_name(table: Tag, headers: list[str]) -> Optional[str]:
    caption = table.find("caption")
    if caption:
        txt = clean_wiki_text(caption.get_text(strip=True))
        if txt:
            return txt

    prev = table
    while prev:
        prev = prev.previous_sibling
        if not isinstance(prev, Tag):
            continue
        if prev.name in {"h2", "h3", "h4"}:
            txt = clean_wiki_text(prev.get_text(strip=True))
            if txt:
                return txt

    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        layout = _layout_from_spanning_header(cells, headers)
        if layout:
            return layout

    return None


def collect_lap_records(
    table: Tag,
    headers: list[str],
    base_layout: Optional[str],
) -> list[dict[str, Any]]:
    lap_scraper = _LAP_RECORDS_CONTEXT or LapRecordsTableScraper()

    all_records: list[dict[str, Any]] = []
    current_layout = base_layout

    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all(["th", "td"])
        if not cells or all(not c.get_text(strip=True) for c in cells):
            continue

        layout = _layout_from_spanning_header(cells, headers)
        if layout:
            current_layout = layout
            continue

        cleaned_cells = [clean_wiki_text(c.get_text(strip=True)) for c in cells]
        if is_repeated_header_row(cleaned_cells, headers):
            logger.debug("Pomijam powtórzony wiersz nagłówka w tabeli rekordów.")
            continue

        row_records = lap_scraper.parse_multi_row(tr, cells, headers)
        if not row_records:
            continue

        layout_name = current_layout or base_layout
        for record in row_records:
            if not record:
                continue
            if layout_name:
                record.setdefault("layout", layout_name)
            all_records.append(record)

    return all_records


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

    def _fetch_soup(self, url: str) -> BeautifulSoup:
        # --- download + error handling spójny z F1Scraper ---
        self.url = url
        try:
            return BeautifulSoup(self._download(), "html.parser")
        except ScraperError as exc:  # type: ignore[misc]
            if self._handle_scraper_error(exc):
                return BeautifulSoup("", "html.parser")
            raise
        except Exception as exc:
            raise self._wrap_network_error(exc) from exc

    def _select_section(
        self,
        soup: BeautifulSoup,
        fragment: Optional[str],
    ) -> BeautifulSoup:
        if not fragment:
            return soup

        section = self._extract_section_by_id(soup, fragment)
        return section or soup

    def _download(self) -> str:
        if not self.url:
            raise ScraperParseError("URL must be set before downloading")
        return self.fetcher.get_text(self.url, timeout=self.timeout)

    def _parse_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        return {
            "infobox": self._scrape_infobox(soup),
            "tables": self._scrape_tables(soup),
        }

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return [
            {
                "url": self._original_url or self.url,
                **self._parse_details(soup),
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
        global _LAP_RECORDS_CONTEXT
        lap_scraper = LapRecordsTableScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                policy=self.policy,
            ),
        )
        lap_scraper.url = self.url  # żeby _full_url działało poprawnie
        all_records: List[Dict[str, Any]] = []
        _LAP_RECORDS_CONTEXT = lap_scraper

        for table in soup.find_all("table", class_="wikitable"):
            header_row = table.find("tr")
            if not header_row:
                continue

            header_cells = header_row.find_all(["th", "td"])
            headers = [clean_wiki_text(c.get_text(strip=True)) for c in header_cells]

            if not is_lap_record_table(headers):
                continue

            base_layout = detect_layout_name(table, headers)
            all_records.extend(collect_lap_records(table, headers, base_layout))

        _LAP_RECORDS_CONTEXT = None

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
