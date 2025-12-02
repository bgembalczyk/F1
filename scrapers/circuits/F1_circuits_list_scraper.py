from __future__ import annotations


from scrapers.F1_table_scraper import F1TableScraper
from scrapers.helpers.columns.columns import (
    SkipColumn,
    SeasonsColumn,
    IntColumn,
    MultiColumn,
    UrlColumn,
    EnumMarksColumn,
    RegexColumn,
    LinksListColumn,
)


class F1CircuitsListScraper(F1TableScraper):
    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    (duża tabela 'Circuits')
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_circuits"
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


if __name__ == "__main__":
    scraper = F1CircuitsListScraper(include_urls=True)

    circuits = scraper.fetch()
    print(f"Pobrano rekordów: {len(circuits)}")

    scraper.to_json("../../data/wiki/circuits/f1_circuits.json")
    scraper.to_csv("../../data/wiki/circuits/f1_circuits.csv")
