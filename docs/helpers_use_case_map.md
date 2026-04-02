# Mapa modułów po migracji `helpers.py` (use-case -> plik)

Poniższa mapa wskazuje docelowe moduły funkcjonalne, do których przeniesiono logikę z ogólnych `helpers.py`.

## layers

- Orkiestracja runnerów / mapy konfiguracji -> `layers/orchestration/runner_maps.py`
- Walidacja i budowa rejestru seedów -> `layers/seed/registry/registry_validation.py`
- Ekstrakcja `name/link` z rekordów seed -> `layers/seed/record_extraction.py`
- Budowanie ścieżek i debug run profile dla layer 0 -> `layers/zero/run_paths.py`

## models

- Rozpoznawanie kontraktu i mapowanie rekordu -> `models/contracts/contract_resolution.py`
- Normalizacja tekstu i ISO we value objects -> `models/value_objects/text_normalization.py`
- Sanityzacja rekordów (split/parse/prune dat) -> `models/services/record_sanitization.py`
- Normalizacja pól w factory rekordów -> `models/records/factories/field_normalization.py`
- Walidacja wartości i zakresów -> `models/validation/value_validation.py`

## scrapers

- Rozdzielanie serii w kolumnach kierowców -> `scrapers/drivers/columns/series_splitting.py`
- Parsowanie rekordów bazowych (visible text, unit list, entries/starts) -> `scrapers/base/parsers/record_parsing.py`
- Normalizacja sekund we value objects -> `scrapers/base/helpers/value_objects/seconds_normalization.py`
- Parsowanie infoboxu z `BeautifulSoup` -> `scrapers/base/infobox/infobox_parsing.py`
- Aplikacja pipeline transformerów -> `scrapers/base/transformers/transformer_application.py`
- Eksport pełnych sezonów -> `scrapers/seasons/season_export.py`
- Notatki wyników wyścigów -> `scrapers/seasons/columns/helpers/race_result/result_notes.py`
- Profile i aliasy sekcji wiki -> `scrapers/wiki/parsers/sections/section_profiles.py`

## Status kompatybilności

- Dotychczasowe moduły `helpers.py` pozostają tymczasowo jako cienkie shimy re-export i są oznaczone jako **deprecated**.
