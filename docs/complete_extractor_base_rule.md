# Reguła dla complete extractorów

Każdy nowy complete extractor (flow: lista + szczegóły) **musi** korzystać z
kanonicznego modułu `scrapers.base.complete_extractor` i dziedziczyć po
`CompleteExtractorBase` importowanym właśnie stamtąd.

## Oficjalna ścieżka importu

```python
from scrapers.base.complete_extractor import CompleteExtractorBase
from scrapers.base.complete_extractor import CompleteExtractorDomainConfig
```

Historyczne importy z pakietu top-level `complete_extractor` pozostają tylko
aliasami kompatybilności i nie powinny być używane w nowym kodzie.

## Wymagane hooki domenowe

- `build_list_scraper(options)` albo (dla przypadków wielolistowych) `build_list_scrapers(options)`.
- `build_single_scraper(options)`.
- `extract_detail_url(record)` albo konfiguracja `DOMAIN_CONFIG.detail_url_field_path`.

## Domyślne zachowanie z bazy

- Konfiguracja `ScraperOptions` z `include_urls=True`.
- Spięcie wspólnej polityki HTTP i `source_adapter` dla scraperów listy/szczegółów.
- Domyślne `assemble_record` delegowane do `DOMAIN_CONFIG.record_assembly_strategy`.
- Wspólna obsługa adapterów:
  - `IterableSourceAdapter` (jedna lista),
  - `MultiIterableSourceAdapter` (wiele list).
