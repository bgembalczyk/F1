from __future__ import annotations

from scrapers.base.table.columns.types.enum_marks import EnumMarksColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.regex import RegexColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper


class F1CircuitsListScraper(F1TableScraper):
    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    (duża tabela 'Circuits')
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_circuits"
    data_resource = "circuits"
    data_file_stem = "f1_circuits"
    section_id = "Circuits"

    expected_headers = [
        "Circuit",
        "Type",
        "Location",
        "Country",
    ]

    column_map = {
        "Circuit": "circuit",
        "Map": "map",
        "Type": "type",
        "Direction": "direction",
        "Location": "location",
        "Country": "country",
        "Last length used": "last_length_used",
        "Turns": "turns",
        "Grands Prix": "grands_prix",
        "Season(s)": "seasons",
        "Grands Prix held": "grands_prix_held",
    }

    # klucz/nagłówek -> kolumna
    columns = {
        # proste kolumny
        "map": SkipColumn(),
        "seasons": SeasonsColumn(),
        "turns": IntColumn(),
        "grands_prix_held": IntColumn(),
        # Circuit → MultiColumn: circuit (url) + circuit_status (enum z raw_text)
        "circuit": MultiColumn(
            {
                "circuit": UrlColumn(),  # już czyści tekst
                "circuit_status": EnumMarksColumn(
                    {"*": "current", "†": "future"},
                    default="former",
                ),
            }
        ),
        # Last length used → MultiColumn: km + mi z jednego raw_text
        # Last length used → MultiColumn: km + mi z tego samego tekstu
        "last_length_used": MultiColumn(
            {
                # "3.780 km (2.349 mi)" -> 3.780
                "last_length_used_km": RegexColumn(
                    r"([\d\.,]+)\s*km",
                    cast=float,
                    normalize_number=True,
                ),
                # "3.780 km (2.349 mi)" -> 2.349
                "last_length_used_mi": RegexColumn(
                    r"\(([\d\.,]+)\s*mi\)",
                    cast=float,
                    normalize_number=True,
                ),
            }
        ),
        # Grands Prix → lista linków bez znaczników
        "grands_prix": LinksListColumn(),
        # alternatywnie: LinksListColumn() + mała modyfikacja tekstu w osobnej kolumnie
    }
