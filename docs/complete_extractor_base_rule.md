# Reguła dla complete extractorów

Każdy nowy complete extractor (flow: lista + szczegóły) **musi** dziedziczyć po
`CompleteExtractorBase` z `scrapers/base/complete_extractor_base.py`.

## Wymagane hooki domenowe

- `build_list_scraper(options)` albo (dla przypadków wielolistowych) `build_list_scrapers(options)`.
- `build_single_scraper(options)`.
- `extract_detail_url(record)`.

## Domyślne zachowanie z bazy

- Konfiguracja `ScraperOptions` z `include_urls=True`.
- Spięcie wspólnej polityki HTTP i `source_adapter` dla scraperów listy/szczegółów.
- Domyślne `assemble_record`: `record + details`.
- Wspólna obsługa adapterów:
  - `IterableSourceAdapter` (jedna lista),
  - `MultiIterableSourceAdapter` (wiele list).
