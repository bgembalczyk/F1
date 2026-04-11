# Scrapers base namespace migration map

Kanoniczny root importów: `scrapers.*` (bez `scrapers.base.*`).

## Status

Migracja zakończona dla aliasów modułów nazwanych: używamy wyłącznie ścieżek kanonicznych.

## Kanoniczne moduły domenowe

- `scrapers.list_scraper_drivers`
- `scrapers.list_scraper_seasons`
- `scrapers.list_scraper_grands_prix`
- `scrapers.single_scraper_drivers`
- `scrapers.constructors_single_scraper`
- `scrapers.circuits_single_scraper`
- `scrapers.single_scraper_seasons`
- `scrapers.single_scraper_grands_prix`

## Mapa migracji importów `scrapers.base.*`

Poniżej widok per grupa modułów (stan aktualny):

- `table`: 62 wystąpienia
- `single article`: 10 wystąpień
- `factory`: 20 wystąpień
- `helpers`: 2 wystąpienia
- `validators`: 0 wystąpień
