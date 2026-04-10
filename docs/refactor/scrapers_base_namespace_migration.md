# Scrapers base namespace migration map

Kanoniczny root importów: `scrapers.*` (bez `scrapers.base.*`).

## 1) Mapowanie modułów nazwanych (source: `scrapers/module_naming_aliases.py`)

- `scrapers.list_scraper_drivers` -> `scrapers.drivers_list_scraper`
- `scrapers.list_scraper_seasons` -> `scrapers.seasons_list_scraper`
- `scrapers.list_scraper_grands_prix` -> `scrapers.grands_prix_list_scraper`
- `scrapers.single_scraper_drivers` -> `scrapers.drivers_detail_scraper`
- `scrapers.constructors_single_scraper` -> `scrapers.constructors_detail_scraper`
- `scrapers.circuits_single_scraper` -> `scrapers.circuits_detail_scraper`
- `scrapers.single_scraper_seasons` -> `scrapers.seasons_detail_scraper`
- `scrapers.single_scraper_grands_prix` -> `scrapers.grands_prix_detail_scraper`

## 2) Mapa migracji importów `scrapers.base.*` (source: `rg "scrapers\\.base\\." scrapers -n`)

Poniżej widok per grupa modułów (po migracji wykonanej w tym kroku):

- `table`: 62 wystąpienia
- `single article`: 10 wystąpień
- `factory`: 20 wystąpień
- `helpers`: 2 wystąpienia
- `validators`: 0 wystąpień

Priorytet migracji: `validators` -> `helpers` -> `single article` -> `factory` -> `table`.
