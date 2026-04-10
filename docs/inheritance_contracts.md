# Kontrakty dziedziczenia runtime

## Linia bazowa

1. `BaseRuntimeComponent` — wspólny runtime (`logger`, `options`, `run context`, `source_adapter`).
2. `BaseScraper` — kontrakt scrapera (`fetch`, `parse`, `build_result`).
3. `BaseCompositeExtractor` — kontrakt ekstraktora orkiestrującego wiele scraperów.

## Reguły nazewnictwa i dziedziczenia

- Klasa kończąca się na `Scraper` dziedziczy po linii scrapera (`BaseScraper`/`ABCScraper` i pochodne).
- Klasa kończąca się na `Extractor` dziedziczy po linii extractorów (`BaseCompositeExtractor`/`CompositeDataExtractor` i pochodne).
- Niedozwolone jest mieszanie baz scraperów i extractorów w jednej klasie.

## Kontrakt metod

### `BaseScraper`
- `fetch() -> list[ExportRecord]` — uruchamia pełny lifecycle pobrania i parsowania.
- `parse(soup: BeautifulSoup) -> list[RawRecord]` — mapuje HTML do rekordów surowych.
- `build_result(data: list[ExportRecord] | None) -> ScrapeResult` — opakowuje dane i metadata źródła.

### `BaseCompositeExtractor`
- `fetch() -> list[Any]` — wykonuje orkiestrację wielu scraperów i zwraca listę rekordów.
- `build_result(data: list[Any] | None) -> ScrapeResult` — eksportowalny wynik ze źródłem.

## Obowiązkowe atrybuty runtime

- `logger`
- `options`
- `_run_id`
- `_data`
- `source_adapter`
- `http_policy`
