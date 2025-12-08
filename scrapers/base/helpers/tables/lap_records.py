from typing import Optional, List, Dict, Any

from bs4 import BeautifulSoup

from scrapers.base.table.columns.types.date import DateColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.time import TimeColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper


class LapRecordsTableScraper(F1TableScraper):
    """
    Lekki scraper pojedynczej tabeli z rekordami okrążeń.

    Używany tylko jako helper w F1SingleCircuitScraper – korzystamy z całej
    logiki kolumn / ColumnContext / extract_links_from_cell itd.
    """

    # Nie wiążemy się z żadną konkretną sekcją
    section_id: Optional[str] = None

    # Minimalny zestaw nagłówków, żeby uznać tabelę za „rekordową”.
    # (kolejność nie ma znaczenia)
    expected_headers = [
        "Time",
    ]

    # mapowanie oryginalnych nagłówków → klucze w rekordzie
    column_map = {
        "Category": "category",
        "Class": "class_",
        "Driver": "driver",
        "Driver/Rider": "driver_rider",
        "Vehicle": "vehicle",
        "Event": "event",
        "Time": "time",
        "Date": "date",
    }

    columns = {
        # Tekst + link (jeśli jest)
        "category": UrlColumn(),
        "class_": UrlColumn(),
        "driver": DriverColumn(),
        "driver_rider": DriverColumn(),
        "vehicle": UrlColumn(),
        "event": UrlColumn(),
        # Nowe kolumny – parsują tekst do ustandaryzowanej postaci
        "time": TimeColumn(),
        "date": DateColumn(),
    }

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Nie używamy standardowego fetch()/_parse_soup – w F1SingleCircuitScraper
        sami podajemy konkretne tabele i nagłówki i wołamy parse_row().
        Metoda zostaje tylko po to, żeby klasa była kompletna.
        """
        raise NotImplementedError(
            "_LapRecordsTableScraper nie jest używany bezpośrednio – "
            "korzystaj z parse_row() na konkretnych tabelach."
        )
