# Debug dumpy scraperów

## Kontrakt `debug_mode` (jedno źródło prawdy)

Tryb debug jest centralnie definiowany przez `scrapers/base/debug_contract.py` i
przenoszony w `RunConfig(debug_mode=...)`.

- `off`:
  - log level: `WARNING`
  - verbosity: 0
  - dumpy: wyłączone
  - `debug_dir`: niewymuszony
- `verbose`:
  - log level: `INFO`
  - verbosity: 1
  - dumpy: wyłączone
  - `debug_dir`: niewymuszony
- `trace`:
  - log level: `DEBUG`
  - verbosity: 2
  - dumpy: włączone
  - `debug_dir`: wymagany

Executory warstw (`LayerZeroExecutor`, `LayerOneExecutor`) walidują ten kontrakt
przed uruchomieniem runnerów.

## Gdzie powstają dumpy?

Scrapery, które uruchamiasz z `RunConfig(debug_dir=...)`, zapisują dumpy błędów
parsowania tabel do katalogu wskazanego przez `debug_dir`.

W konfiguracjach dla złożonych scraperów (`drivers/`, `constructors/`, `circuits/`)
ustawiamy domyślnie:

```
data/debug/
```

Dumpy to pliki JSON o nazwach podobnych do:

```
table_pipeline_20240101T120000Z_abcdef123456.json
```

Każdy dump zawiera kontekst błędu (URL, section_id, header, row_index, run_id)
oraz surowy HTML komórki.

## Cache a debug

Jeśli uruchamiasz scraper z cache (`RunConfig(cache_dir=..., cache_ttl=...)`),
to debug dumpy mogą pochodzić z HTML-a pobranego z cache. W przypadku analizy
świeżych danych lub problemów reprodukcji, wyczyść katalog cache albo ustaw
`cache_ttl=0`, aby wymusić ponowne pobranie strony.

## Jak usuwać / rotować dumpy?

- Ręcznie: usuń cały katalog `data/debug/` lub wybrane pliki.
- Automatycznie (przykład rotacji po 7 dniach):

```
find data/debug -type f -mtime +7 -delete
```

Możesz też zautomatyzować rotację za pomocą crona lub innego harmonogramu
zależnie od środowiska, w którym uruchamiasz scrapery.
