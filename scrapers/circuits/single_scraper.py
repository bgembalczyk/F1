from __future__ import annotations

from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.helpers.html_utils import clean_wiki_text
from scrapers.base.infobox.circuits.scraper import F1CircuitInfoboxScraper
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper
from scrapers.base.errors import ScraperError, ScraperParseError


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
        options = options or ScraperOptions()

        # Ten scraper zawsze potrzebuje URL-i (lap records, encje itd.)
        options.include_urls = True

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

    def _is_circuit_like_article(self, soup: BeautifulSoup) -> bool:
        """Sprawdza, czy artykuł wygląda na tor/tor wyścigowy po kategoriach."""
        cat_div = soup.find("div", id="mw-normal-catlinks")
        if not cat_div:
            return False

        keywords = [
            "circuit",
            "race track",
            "racetrack",
            "speedway",
            "raceway",
            "motor racing",
        ]
        for a in cat_div.find_all("a"):
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in keywords):
                return True
        return False

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
        return infobox_scraper.parse_from_soup(soup)

    def _scrape_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        lap_scraper = LapRecordsTableScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                policy=self.policy,
            ),
        )
        lap_scraper.url = self.url  # żeby _full_url działało poprawnie

        def guess_table_layout(table: Tag) -> Optional[str]:
            caption = table.find("caption")
            if caption:
                txt = clean_wiki_text(caption.get_text(" ", strip=True))
                if txt:
                    return txt

            prev = table
            while prev:
                prev = prev.previous_sibling
                if not isinstance(prev, Tag):
                    continue
                if prev.name in {"h2", "h3", "h4"}:
                    txt = clean_wiki_text(prev.get_text(" ", strip=True))
                    if txt:
                        return txt
            return None

        all_records: List[Dict[str, Any]] = []

        for table in soup.find_all("table", class_="wikitable"):
            header_row = table.find("tr")
            if not header_row:
                continue

            header_cells = header_row.find_all(["th", "td"])
            headers = [
                clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells
            ]

            if not lap_scraper.headers_match(headers):
                header_set = set(headers)
                if not (
                    "Time" in header_set
                    and ("Driver" in header_set or "Driver/Rider" in header_set)
                ):
                    continue

            base_layout = guess_table_layout(table)
            current_layout = base_layout

            for tr in table.find_all("tr")[1:]:
                cells = tr.find_all(["th", "td"])
                if not cells or all(not c.get_text(strip=True) for c in cells):
                    continue

                th_only = all(c.name == "th" for c in cells)
                td_only = all(c.name == "td" for c in cells)

                if th_only and not td_only and len(cells) == 1:
                    th = cells[0]
                    try:
                        colspan = int(th.get("colspan", "1"))
                    except ValueError:
                        colspan = 1

                    text = clean_wiki_text(th.get_text(" ", strip=True))
                    if colspan >= len(headers) or any(
                        kw in (text or "").lower()
                        for kw in (
                            "circuit",
                            "layout",
                            "course",
                            "km",
                            "mi",
                            "present",
                            "configuration",
                        )
                    ):
                        if text:
                            current_layout = text
                        continue

                cleaned_cells = [
                    clean_wiki_text(c.get_text(" ", strip=True)) for c in cells
                ]
                if len(cleaned_cells) == len(headers) and cleaned_cells == list(
                    headers
                ):
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

        # Grupowanie po layoutach (sumarycznie z wszystkich tabel)
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
