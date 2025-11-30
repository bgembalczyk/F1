from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

try:
    import pandas as pd

    _HAS_PANDAS = True
except Exception:  # opcjonalne
    _HAS_PANDAS = False


# ======================================================================
# BAZA
# ======================================================================


class F1Scraper(ABC):
    """
    Bazowa klasa dla wszystkich scrapperów F1.

    Odpowiada za:
    - pobranie HTML (requests)
    - trzymanie danych w pamięci
    - eksport do JSON / CSV / DataFrame
    - szablon metody fetch()
    """

    #: Pełny URL strony Wikipedii
    url: str

    def __init__(
        self,
        *,
        include_urls: bool = True,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.include_urls = include_urls
        self.session = session or requests.Session()
        self._data: List[Dict[str, Any]] = []

    # ---------- API wysokiego poziomu ----------

    def fetch(self) -> List[Dict[str, Any]]:
        """Pobierz dane z sieci i sparsuj je do listy słowników."""
        html = self._download()
        soup = BeautifulSoup(html, "html.parser")
        self._data = self._parse_soup(soup)
        return self._data

    def get_data(self) -> List[Dict[str, Any]]:
        """Zwróć dane – jeśli jeszcze nie ma, uruchom fetch()."""
        if not self._data:
            self.fetch()
        return self._data

    # ---------- Eksport ----------

    def to_json(self, path: str | Path, *, indent: int = 2) -> None:
        data = self.get_data()
        path = Path(path)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding="utf-8")

    def to_csv(self, path: str | Path, *, fieldnames: Optional[Sequence[str]] = None) -> None:
        data = self.get_data()
        if not data:
            return

        path = Path(path)

        # Jeżeli nie podano fieldnames – bierzemy wszystkie klucze z unią
        if fieldnames is None:
            keys: List[str] = []
            for row in data:
                for k in row.keys():
                    if k not in keys:
                        keys.append(k)
            fieldnames = keys

        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

    def to_dataframe(self):
        if not _HAS_PANDAS:
            raise RuntimeError("Pandas nie jest zainstalowane.")
        return pd.DataFrame(self.get_data())

    # ---------- Metody wewnętrzne ----------

    def _download(self) -> str:
        resp = self.session.get(self.url)
        resp.raise_for_status()
        return resp.text

    @abstractmethod
    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parsowanie BS4 -> lista rekordów."""
        raise NotImplementedError

    # ---------- Pomocnicze ----------

    def _full_url(self, href: str | None) -> Optional[str]:
        if not href:
            return None
        # Linki wewnętrzne z Wikipedii typu "/wiki/..."
        return urljoin(self.url, href)


# ======================================================================
# SCRAPERY TABEL
# ======================================================================




# ======================================================================
# SCRAPERY LIST
# ======================================================================




# ======================================================================
# PRZYKŁADOWE KOŃCOWE SCRAPERY (Twoje konkretne)
# ======================================================================


    # domyślne parse_row z F1TableScraper jest OK
















