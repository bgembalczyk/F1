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

## Oficjalny kontrakt hooków dla scraperów szczegółów

Dla klas dziedziczących po `SingleWikiArticleScraperBase` i
`SingleWikiArticleSectionAdapterBase` obowiązuje wyłącznie poniższy słownik
hooków (`SingleWikiArticleScraperBase.STANDARD_HOOKS`):

- `_build_infobox_payload`
- `_build_tables_payload`
- `_build_sections_payload`
- `_assemble_record`

Nowe klasy domenowe powinny implementować tylko te nazwy. Wprowadzanie aliasów
(np. `build_infobox_payload`, `_prepare_infobox_payload`, `assemble_record`)
jest zabronione, chyba że w kodzie dodano jawne uzasadnienie komentarzem
`hook-name-allow: ...`.

Reguła jest automatycznie egzekwowana przez skrypt:

- `python scripts/check_single_wiki_hook_names.py`
