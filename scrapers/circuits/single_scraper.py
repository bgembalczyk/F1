from typing import Optional, Dict, Any, List

import requests
from bs4 import BeautifulSoup, Tag

from http_client.interfaces import HttpClientProtocol
from scrapers.base.helpers.tables.lap_records import LapRecordsTableScraper
from scrapers.base.helpers.utils import clean_wiki_text
from scrapers.base.infobox.circuits.scraper import F1CircuitInfoboxScraper
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.scraper import F1Scraper, ScraperOptions


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
        session: Optional[requests.Session] = None,
        http_client: Optional[HttpClientProtocol] = None,
        timeout: int = 10,
        headers: Optional[Dict[str, str]] = None,
        options: ScraperOptions | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            options=options,
            session=session,
            headers=headers,
            http_client=http_client,
            timeout=timeout,
            **kwargs,
        )
        self.timeout = timeout
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

        # rozbijamy ewentualny fragment po "#"
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        self.url = base_url

        soup_full = BeautifulSoup(self._download(), "html.parser")

        # 1) filtr po kategoriach – jeżeli to nie wygląda na tor, nie scrapujemy dalej
        if not self._is_circuit_like_article(soup_full):
            return None

        # 2) jeśli mamy fragment, zawężamy się do danej sekcji
        working_soup = soup_full
        if fragment:
            section = self._extract_section_by_id(soup_full, fragment)
            if section is not None:
                working_soup = section

        parsed = self._parse_soup(working_soup)
        return parsed[0] if parsed else None

    def _download(self) -> str:
        if not self.url:
            raise ValueError("URL must be set before downloading")

        return self.http_client.get_text(self.url, timeout=self.timeout)

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

        Logika filtrowania po kategoriach i zawężania do sekcji (#fragment)
        jest załatwiona na poziomie F1SingleCircuitScraper.fetch,
        więc tutaj po prostu parsujemy przekazany fragment drzewa.
        """
        infobox_scraper = F1CircuitInfoboxScraper(
            options=self.options,
            timeout=self.timeout,
            http_client=self.http_client,
        )
        return infobox_scraper.parse_from_soup(soup)

    def _scrape_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Zbiera tabele z najszybszymi okrążeniami („lap records / fastest laps”).

        Zasady:
        - przeglądamy wszystkie 'wikitable' na stronie,
        - bierzemy tylko te, które mają nagłówki odpowiadające rekordom okrążeń,
        - jeżeli w tabeli występują wiersze <th colspan="..."> – traktujemy je
          jako nagłówki layoutów i przypisujemy ten layout do kolejnych wierszy
          z danymi,
        - jeżeli layout jest w captionie lub nagłówku nad tabelą – używamy go
          jako domyślnej nazwy layoutu,
        - każdy rekord dostaje pole 'layout' (string) – dzięki temu możesz
          łatwo zgrupować wyniki po layoutach.
        """
        lap_scraper = LapRecordsTableScraper(
            options=self.options,
            http_client=self.http_client,  # <<< kluczowa zmiana
        )
        lap_scraper.url = self.url  # żeby _full_url działało poprawnie

        results: List[Dict[str, Any]] = []

        # --- pomocnicza funkcja: zgadnij domyślną nazwę layoutu dla tabeli ---
        def guess_table_layout(table: Tag) -> Optional[str]:
            # 1) caption
            caption = table.find("caption")
            if caption:
                txt = clean_wiki_text(caption.get_text(" ", strip=True))
                if txt:
                    return txt

            # 2) najbliższy poprzedni nagłówek (h2/h3/h4)
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

        # --- iteracja po wszystkich kandydatach na tabele z rekordami ---
        for table in soup.find_all("table", class_="wikitable"):
            header_row = table.find("tr")
            if not header_row:
                continue

            header_cells = header_row.find_all(["th", "td"])
            headers = [
                clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells
            ]

            # czy ta tabela wygląda jak rekordy okrążeń?
            if not lap_scraper._headers_match(headers):
                # dodatkowa heurystyka: niektóre tabele mogą mieć np. „Driver/Rider”
                header_set = set(headers)
                if not (
                    "Time" in header_set
                    and ("Driver" in header_set or "Driver/Rider" in header_set)
                ):
                    continue  # nie wygląda jak rekordy

            base_layout = guess_table_layout(table)
            current_layout = base_layout

            # iterujemy po wierszach danych (pomijamy pierwszy z nagłówkami)
            for tr in table.find_all("tr")[1:]:
                cells = tr.find_all(["th", "td"])

                # puste / ozdobne wiersze ignorujemy
                if not cells or all(not c.get_text(strip=True) for c in cells):
                    continue

                # --- 1) wiersz nagłówka layoutu: <tr><th colspan="...">Layout...</th></tr> ---
                th_only = all(c.name == "th" for c in cells)
                td_only = all(c.name == "td" for c in cells)

                if th_only and not td_only and len(cells) == 1:
                    th = cells[0]
                    try:
                        colspan = int(th.get("colspan", "1"))
                    except ValueError:
                        colspan = 1

                    text = clean_wiki_text(th.get_text(" ", strip=True))

                    # traktujemy jako nagłówek layoutu, jeśli:
                    # - colspan >= liczba kolumn nagłówka
                    # - albo w tekście widać, że to layout (np. "Circuit", "Layout", "km", "mi", "present" itd.)
                    if colspan >= len(headers) or any(
                        kw in (text or "").lower()
                        for kw in [
                            "circuit",
                            "layout",
                            "course",
                            "km",
                            "mi",
                            "present",
                            "configuration",
                        ]
                    ):
                        if text:
                            current_layout = text
                        continue  # nie parsujemy tego wiersza jako danych

                # --- 2) powtórzony nagłówek – ignorujemy (częsty pattern w wiki) ---
                cleaned_cells = [
                    clean_wiki_text(c.get_text(" ", strip=True)) for c in cells
                ]
                if len(cleaned_cells) == len(headers) and cleaned_cells == list(
                    headers
                ):
                    continue

                # --- 3) normalny wiersz z danymi ---
                # może zawierać wiele rekordów logicznych rozdzielonych <br>
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

            # --- grupowanie po layoutach ---
            layouts: Dict[str, List[Dict[str, Any]]] = {}
            for rec in results:
                layout_name = rec.get("layout")
                if not layout_name:
                    # interesują nas tylko rekordy, w których layout udało się ustalić
                    continue

                # nie powielamy layoutu w środku rekordu
                rec_copy = dict(rec)
                rec_copy.pop("layout", None)

                if layout_name not in layouts:
                    layouts[layout_name] = []
                layouts[layout_name].append(rec_copy)

            # tables = lista layoutów, każdy z listą rekordów (najszybszych czasów)
            grouped = [
                {
                    "layout": layout_name,
                    "lap_records": recs,
                }
                for layout_name, recs in layouts.items()
            ]

            return grouped
