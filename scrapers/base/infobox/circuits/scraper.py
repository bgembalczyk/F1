from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

from http_client import HttpClient
from scrapers.base.infobox.mixins.circuits.entities import CircuitEntitiesMixin
from scrapers.base.infobox.mixins.circuits.layouts import CircuitInfoboxLayoutsMixin
from scrapers.base.infobox.scraper import WikipediaInfoboxScraper
from scrapers.base.scraper import F1Scraper


class F1CircuitInfoboxScraper(
    CircuitEntitiesMixin, CircuitInfoboxLayoutsMixin, F1Scraper, WikipediaInfoboxScraper
):
    """Parser infoboksów torów F1 z heurystykami pod typowe pola."""

    def __init__(
        self,
        *,
        timeout: int = 10,
        include_urls: bool = True,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClient] = None,
    ) -> None:
        F1Scraper.__init__(
            self,
            include_urls=include_urls,
            session=session,
            headers=headers,
            http_client=http_client,
            timeout=timeout,
        )
        WikipediaInfoboxScraper.__init__(
            self,
            timeout=timeout,
            session=self.session,
            headers=headers,
            http_client=self.http_client,
        )
        self.url: str = ""

    # ------------------------------
    # Publiczne API
    # ------------------------------

    def fetch(self, url: str) -> Dict[str, Any]:
        """
        Główne API używane wewnętrznie – obsługuje #fragment (sekcje),
        przycina infoboksy po infobox-full-data itd.
        """
        self.url = url
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        self.url = base_url

        html = self._download()
        full_soup = BeautifulSoup(html, "html.parser")

        if not self._is_circuit_like_article(full_soup):
            title = full_soup.title.get_text(strip=True) if full_soup.title else None
            return self._prune_nulls(
                {
                    "url": url,
                    "title": title,
                },
            )

        soup = full_soup
        if fragment:
            section = self._extract_section_by_id(full_soup, fragment)
            if section is not None:
                soup = section

        return self.parse_from_soup(soup)

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """API bazowej klasy – deleguje do parse_from_soup."""
        return [self.parse_from_soup(soup)]

    # >>> ZMIANA TUTAJ <<<
    def parse_from_soup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Zwraca znormalizowany infobox + layouts (bez surowego `rows`).

        Od pierwszego wiersza z class="infobox-full-data" w danej tabeli
        infoboksa ignorujemy resztę wierszy (wycinamy je z DOM-u),
        żeby nie mieszać danych z pełnotabelarycznymi statystykami.
        """
        truncated_soup = self._truncate_infobox_after_full_data(soup)

        # parsujemy infobox już bez "ogonów" po infobox-full-data
        raw = super().parse_from_soup(truncated_soup)

        # layouty wciąż parsujemy z pełnej sekcji artykułu
        layout_records = self._parse_layout_sections(soup)
        return self._with_normalized(raw, layout_records)

    # ------------------------------
    # Helper: przycinanie infoboksa
    # ------------------------------

    def _truncate_infobox_after_full_data(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        W każdej tabeli infoboksa usuwamy:
        - pierwszy wiersz, który ma klasę `infobox-full-data`
          LUB zawiera komórkę (td/th) z tą klasą,
        - wszystkie kolejne wiersze poniżej.
        """

        # helper: tabela ma mieć klasę zawierającą 'infobox'
        def _has_infobox_class(classes: Any) -> bool:
            if not classes:
                return False
            if isinstance(classes, str):
                classes = classes.split()
            return "infobox" in classes

        # każda tabela infoboksa
        for table in soup.find_all("table", class_=_has_infobox_class):
            rows: List[Tag] = table.find_all("tr")

            cut_index: Optional[int] = None
            for idx, row in enumerate(rows):
                row_classes = row.get("class") or []
                if isinstance(row_classes, str):
                    row_classes = row_classes.split()

                has_full_on_tr = "infobox-full-data" in row_classes
                has_full_in_cell = row.find(["td", "th"], class_="infobox-full-data") is not None

                if has_full_on_tr or has_full_in_cell:
                    cut_index = idx
                    break

            # jeśli znaleziono początek sekcji 'full-data' → usuń wszystko od tego miejsca
            if cut_index is not None:
                for r in rows[cut_index:]:
                    r.decompose()

        return soup

    # ------------------------------
    # Pobieranie / sekcje / kategorie
    # ------------------------------

    def _download(self) -> str:
        if not self.url:
            raise ValueError("URL must be set before downloading")
        response = self.session.get(self.url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _is_circuit_like_article(self, soup: BeautifulSoup) -> bool:
        """Sprawdza czy artykuł wygląda na tor/tor wyścigowy po kategoriach."""
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
            "motorsport venue",
        ]
        for a in cat_div.find_all("a"):
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in keywords):
                return True
        return False

    def _extract_section_by_id(
        self, soup: BeautifulSoup, fragment: str
    ) -> Optional[BeautifulSoup]:
        """
        Zwraca pod-drzewo odpowiadające sekcji o nagłówku powiązanym z `fragment`.

        1) Próbuje znaleźć element o id=fragment (oraz warianty z _ / spacjami).
        2) Jeśli się nie uda – szuka nagłówka po tekście (np. "Bugatti Circuit").
        3) Sekcję definiuje jako:
           [blok nagłówka] + wszystkie rodzeństwa aż do kolejnego nagłówka
           TEGO SAMEGO poziomu (hN).
        """

        # --- 1) znajdź węzeł po id (z normalizacją _) ---
        candidates = {fragment}
        candidates.add(fragment.replace(" ", "_"))
        candidates.add(fragment.replace("_", " "))

        node: Optional[Tag] = None
        for cand in candidates:
            node = soup.find(id=cand)
            if node:
                break

        header: Optional[Tag] = None

        if node:
            if node.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                header = node
            else:
                header = node.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"])

        # --- 2) fallback: szukanie nagłówka po tekście ---
        if header is None:
            target_text = fragment.replace("_", " ").strip().lower()

            for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                full_text = (h.get_text(strip=True) or "").lower()
                if full_text == target_text:
                    header = h
                    break

                span = h.find("span", class_="mw-headline")
                if span:
                    span_text = (span.get_text(strip=True) or "").lower()
                    if span_text == target_text:
                        header = h
                        break

        if header is None:
            return None

        # Poziom nagłówka (np. 2 dla h2)
        try:
            header_level = int(header.name[1])
        except (TypeError, ValueError, IndexError):
            header_level = None

        # --- 3) uwzględnij wrapper <div class="mw-heading ..."> jeśli jest ---
        heading_block: Tag = header
        parent = header.parent
        if isinstance(parent, Tag):
            classes = parent.get("class") or []
            if "mw-heading" in classes and parent.find(
                header.name, recursive=False
            ) is header:
                heading_block = parent

        # UWAGA: nie przenosimy heading_block do nowego soup-a przed zebraniem rodzeństw.
        collected: List[Any] = [heading_block]

        # --- 4) zbierz rodzeństwa aż do nagłówka tego samego poziomu ---
        for sib in heading_block.next_siblings:
            if isinstance(sib, Tag):
                same_level_header_tag: Optional[Tag] = None

                # Przypadek 1: nagłówek bez wrappera
                if sib.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    same_level_header_tag = sib

                # Przypadek 2: wrapper <div class="mw-heading ..."><hN>...</hN></div>
                elif "mw-heading" in (sib.get("class") or []):
                    h_child = sib.find(
                        ["h1", "h2", "h3", "h4", "h5", "h6"], recursive=False
                    )
                    if h_child is not None:
                        same_level_header_tag = h_child

                if same_level_header_tag is not None and header_level is not None:
                    try:
                        sib_level = int(same_level_header_tag.name[1])
                    except (TypeError, ValueError, IndexError):
                        sib_level = None

                    if sib_level == header_level:
                        # doszliśmy do następnej sekcji tego samego poziomu
                        break

            collected.append(sib)

        html = "".join(str(node) for node in collected)
        if not html.strip():
            return None

        section_soup = BeautifulSoup(html, "html.parser")
        return section_soup
