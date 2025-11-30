from F1_table_scraper import F1TableScraper


class F1CircuitsScraper(F1TableScraper):
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

    url_columns = ("Circuit",)


if __name__ == "__main__":
    scraper = F1CircuitsScraper(include_urls=True)

    circuits = scraper.fetch()
    print(f"Pobrano rekordów: {len(circuits)}")

    scraper.to_json("f1_circuits.json")
    scraper.to_csv("f1_circuits.csv")
