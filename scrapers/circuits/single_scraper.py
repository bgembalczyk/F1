from __future__ import annotations

from typing import Optional, Dict, Any, List

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.helpers.utils import clean_wiki_text  # <- FIX: spójnie z resztą helperów
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.infobox.circuits.scraper import F1CircuitInfoboxScraper
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper

# PR wnosił ustandaryzowane wyjątki – używamy jeśli są w projekcie.
try:  # pragma: no cover
    from scrapers.base.errors import ScraperError, ScraperParseError
except Exception:  # pragma: no cover
    ScraperError = Exception  # type: ignore[misc,assignment]
    ScraperParseError = ValueError  # type: ignore[misc,assignment]


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

        if options.fetcher is None:
            options.fetcher = HtmlFetcher(
                session=options.session,
                headers=options.headers,
                http_client=options.http_client,
                timeout=options.timeout,
                retries=options.retries,
                cache=options.cache,
            )

        super().__init__(options=options)
        self.timeout = options.timeout
        self.url: str = ""
        self._original_url: Optional[str] = None

    def fetch(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Zwraca dict z kluczami:
        - url     – oryginalny URL (z ewentualnym fragmentem),
        - infobox – wynik F1CircuitInfoboxScraper.parse_from_soup,
        - tables  – lista zparsowanych wikitabel.

        Jeżeli artykuł nie wygląda na tor/tor wyścigowy (brak odpowiednich kategorii),
        zwraca None (nie dokładamy szczegółów).
        """
        self._original_url = url

        base_url, fragment = (url.split("#", 1) + [None])[:2]
        self.url = base_url

        # --- download + error handling spójny z F1Scraper ---
        try:
            soup_full = BeautifulSoup(self._download(), "html.parser")
        except ScraperError as exc:  # type: ignore[misc]
            if self._handle_scraper_error(exc):
                return None
            raise
        except Exception as exc:
            raise self._wrap_network_error(exc) from exc

        # 1) filtr po kategoriach – jeżeli to nie wygląda na tor, nie scrapujemy dalej
        if not self._is_circuit_like_article(soup_full):
            return None

        # 2) jeśli mamy fragment, zawężamy się do danej sekcji
        working_soup = soup_full
        if fragment:
            section = self._extract_section_by_id(soup_full, fragment)
            if section is not None:
                working_soup = section

        try:
            parsed = self._parse_soup(working_soup)
        except ScraperError as exc:  # type: ignore[misc]
            if self._handle_scraper_error(exc):
                return None
            raise
        except Exception as exc:
            parse_error = self._wrap_parse_error(exc)
            if self._handle_scraper_error(parse_error):
                return None
            raise parse_error from exc

        return parsed[0] if parsed else None

    def _download(self) -> str:
        if not self.url:
            raise ScraperParseError("URL must be set before downloading")
        return self.fetcher.get_text(self.url, timeout=self.timeout)

    # ------------------------------
    # Heurystyki: kategorie + sekcje
    # ------------------------------

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

    # ------------------------------
    # Parsowanie treści
    # ------------------------------

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        return [
            {
                "url": self._original_url or self.url,
                "infobox": self._scrape_infobox(soup),
                "tables": self._scrape_tables(soup),
            }
        ]

    def _scrape_infobox(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parsuje infobox toru z przekazanego soup.
        """
        infobox_scraper = F1CircuitInfoboxScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                fetcher=self.fetcher,
                timeout=self.timeout,
            ),
        )
        return infobox_scraper.parse_from_soup(soup)

    def _scrape_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Zbiera tabele z najszybszymi okrążeniami („lap records / fastest laps”).

        UWAGA: Zwracamy listę layoutów dla *pierwszej* pasującej tabeli (jak w main).
        """
        lap_scraper = LapRecordsTableScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                fetcher=self.fetcher,
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

        for table in soup.find_all("table", class_="wikitable"):
            header_row = table.find("tr")
            if not header_row:
                continue

            header_cells = header_row.find_all(["th", "td"])
            headers = [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]

            if not lap_scraper._headers_match(headers):
                header_set = set(headers)
                if not (
                    "Time" in header_set
                    and ("Driver" in header_set or "Driver/Rider" in header_set)
                ):
                    continue

            base_layout = guess_table_layout(table)
            current_layout = base_layout
            results: List[Dict[str, Any]] = []

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

                cleaned_cells = [clean_wiki_text(c.get_text(" ", strip=True)) for c in cells]
                if len(cleaned_cells) == len(headers) and cleaned_cells == list(headers):
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
                    results.append(record)

            layouts: Dict[str, List[Dict[str, Any]]] = {}
            for rec in results:
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

        return []
