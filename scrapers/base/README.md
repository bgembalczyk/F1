# scrapers/base

## Odpowiedzialność
`scrapers/base` dostarcza fundament pipeline'u scraperów: wspólny lifecycle, kontrakty źródeł, uruchamianie kroków przetwarzania, walidację, logowanie i eksport wyników.

## Punkt wejścia
- Główny punkt wejścia uruchamiania: `ScraperRunner.run_and_export(...)`.
- Główny punkt wejścia dla implementacji nowych scraperów: dziedziczenie po `ABCScraper`.
- Kontrakt konfiguracji uruchomienia: `RunConfig`.

## Najczęstszy punkt debug
Najczęściej debug zaczyna się w `scrapers/base/abc.py` (`fetch()`, `_initialize_runtime()`, `_initialize_pipeline_orchestrator()`) oraz w `scrapers/base/pipeline_runner.py`, gdzie widać kolejność kroków i przekazywane typy wejścia/wyjścia.

Jeśli problem wychodzi dopiero przy zapisie, kolejne miejsce to `scrapers/base/runner.py` (eksport JSON/CSV i ścieżki plików).

## Czego tu nie robić
- Nie doklejać tu logiki specyficznej dla pojedyncych domen/encji (powinna trafić do konkretnego scrapera lub modułu domenowego).
- Nie omijać lifecycle `ABCScraper` przez ręczne wywoływanie kroków pipeline poza kontraktem.
- Nie traktować `scrapers/base` jako magazynu „utilities od wszystkiego” niezwiązanych z pipeline scrapingowym.
- Nie ukrywać błędów jakości danych przez ciche fallbacki w klasach bazowych.
