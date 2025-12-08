# F1 Wikipedia scrapers

Narzędzia do pobierania danych z Wikipedii o Formule 1, pogrupowane w paczce `scrapers`.

## Uruchamianie scraperów

Użyj wspólnego modułu CLI, który ładuje klasę scrapera dynamicznie (po samej nazwie lub pełnej
ścieżce modułu) i zapisuje wyniki w `data/wiki/<zasób>/<plik>.json|csv` na podstawie atrybutów
klasy.

```bash
python tools/run_scraper.py F1DriversListScraper --output-dir data/wiki --no-include-urls
```

Parametr `--output-dir` domyślnie wskazuje na `data/wiki`, a flaga `--include-urls/--no-include-urls`
steruje obecnością URL-i w danych wyjściowych.
