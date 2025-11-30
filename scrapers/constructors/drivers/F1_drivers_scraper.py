from typing import Sequence, Optional, Dict, Any

from bs4 import Tag

from scrapers.F1_table_scraper import F1TableScraper


class F1DriversScraper(F1TableScraper):
    """
    Tabela kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_drivers

    Sekcja: 'Drivers' – główna tabela wszystkich kierowców.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_drivers"
    section_id = "Drivers"

    # Bierzemy podzbiór nagłówków, które na pewno są w tabeli – używane do dopasowania.
    expected_headers = [
        "Driver name",
        "Nationality",
        "Seasons competed",
    ]

    # Mapowanie *prostych* nagłówków -> nasze klucze.
    # Kolumna Points ma dziwnie długi nagłówek, więc obsłużymy ją osobno w parse_row().
    column_map = {
        "Driver name": "driver_name",
        "Nationality": "nationality",
        "Seasons competed": "seasons_competed",
        "Drivers' Championships": "drivers_championships",
        "Race entries": "race_entries",
        "Race starts": "race_starts",
        "Pole positions": "pole_positions",
        "Race wins": "race_wins",
        "Podiums": "podiums",
        "Fastest laps": "fastest_laps",
        # "Points (...)" -> obsługujemy w parse_row przez startswith("Points")
    }

    # Chcemy link do strony kierowcy
    url_columns = ("Driver name",)

    def parse_row(
        self,
        row: Tag,
        cells: Sequence[Tag],
        headers: Sequence[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Nadpisujemy tylko po to, żeby:
        - ładnie nazwać kolumnę z punktami jako 'points',
        - dorzucić URL kierowcy dla Driver name.
        Reszta zachowuje się jak w F1TableScraper.
        """
        record: Dict[str, Any] = {}

        for header, cell in zip(headers, cells):
            # Specjalna obsługa kolumny z punktami – jej nagłówek zaczyna się od "Points"
            if header.startswith("Points"):
                key = "points"
            else:
                key = self.column_map.get(header, self._normalize_header(header))

            text = cell.get_text(" ", strip=True)

            # URL kierowcy z komórki 'Driver name'
            if self.include_urls and header in self.url_columns:
                a = cell.find("a", href=True)
                href = a["href"] if a else None
                full = self._full_url(href)
                if full:
                    record[f"{key}_url"] = full

            record[key] = text

        # Możesz tu dodać jakieś filtry, np. pomijanie pustych wierszy:
        if not record.get("driver_name"):
            return None

        return record
