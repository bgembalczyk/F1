# scrapers/base

## Cel modułu
Wspólne fundamenty scraperów: bazowa klasa scrapera, pipeline transformacji, adaptery źródeł, konfiguracja runa, logowanie i runner eksportujący wyniki.

## Główne klasy
- `ABCScraper` – bazowy lifecycle `download -> parse -> normalize -> transform -> validate -> post_process`.
- `ScraperPipelineRunner` – wykonanie kroków pipeline + raportowanie jakości per krok.
- `ScraperRunner` – tworzenie instancji scrapera i eksport JSON/CSV.
- `SourceAdapter` (+ iterable adaptery) – kontrakty dostarczania źródła danych.

## Co jest publiczne
- Publiczne API konstrukcyjne dla nowych scraperów: dziedziczenie po `ABCScraper`.
- Publiczne API uruchamiania: `ScraperRunner.run_and_export(...)`.
- Publiczny kontrakt konfiguracji: `RunConfig`.

## Gdzie najczęściej debugować
- `scrapers/base/abc.py`: `fetch()`, `_initialize_runtime()`, `_initialize_pipeline_orchestrator()`.
- `scrapers/base/pipeline_runner.py`: kolejność kroków i typ wejścia/wyjścia każdego etapu.
- `scrapers/base/runner.py`: finalny eksport i ścieżki plików.
- `scrapers/base/logging.py`: poziomy logowania i kontekst wykonania (`run_id`, `seed_name`).

## Najczęstsze pułapki
- Brak ustawionego `url` w klasie scrapera kończy się wyjątkiem przed faktycznym fetch.
- Niezgodne typy między krokami pipeline powodują `TypeError` dopiero w runtime.
- `get_data()` może ukryć fakt, że `fetch()` wykonał soft-skip i zwrócił pustą listę.
- Włączenie `include_urls`/normalizacji bez świadomości wpływa na finalne rekordy eksportowe.
