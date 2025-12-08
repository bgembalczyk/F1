from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from bs4 import BeautifulSoup
from urllib.parse import urljoin

import requests

from http_client import HttpClient

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
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClient] = None,
        timeout: int = 10,
        retries: int = 0,
    ) -> None:
        self.include_urls = include_urls
        self.http_client = http_client or HttpClient(
            session=session, headers=headers, timeout=timeout, retries=retries
        )
        self.session = self.http_client.session

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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=indent), encoding="utf-8"
        )

    def to_csv(
        self, path: str | Path, *, fieldnames: Optional[Sequence[str]] = None
    ) -> None:
        data = self.get_data()
        if not data:
            return

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

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

    def export_data(
        self,
        target_dir: str | Path,
        *,
        basename: str,
        fieldnames: Optional[Sequence[str]] = None,
        export_json: bool = True,
        export_csv: bool = True,
        verbose: bool = True,
    ) -> Dict[str, Path]:
        """Eksport danych do JSON/CSV z jednego miejsca.

        Ułatwia tworzenie spójnych ścieżek i komunikatów dla wszystkich
        scraperów korzystających ze wspólnego CLI.
        """

        data = self.get_data()
        if verbose:
            print(f"Pobrano rekordów: {len(data)}")

        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        exported: Dict[str, Path] = {}

        if export_json:
            json_path = target_path / f"{basename}.json"
            self.to_json(json_path)
            exported["json"] = json_path
            if verbose:
                print(f"Zapisano JSON: {json_path}")

        if export_csv:
            csv_path = target_path / f"{basename}.csv"
            self.to_csv(csv_path, fieldnames=fieldnames)
            exported["csv"] = csv_path
            if verbose:
                print(f"Zapisano CSV: {csv_path}")

        return exported

    def to_dataframe(self):
        if not _HAS_PANDAS:
            raise RuntimeError("Pandas nie jest zainstalowane.")
        return pd.DataFrame(self.get_data())

    # ---------- Metody wewnętrzne ----------

    def _download(self) -> str:
        return self.http_client.get_text(self.url)

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
