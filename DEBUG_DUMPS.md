# Debug dumpy scraperów

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

## Jak usuwać / rotować dumpy?

- Ręcznie: usuń cały katalog `data/debug/` lub wybrane pliki.
- Automatycznie (przykład rotacji po 7 dniach):

```
find data/debug -type f -mtime +7 -delete
```

Możesz też zautomatyzować rotację za pomocą crona lub innego harmonogramu
zależnie od środowiska, w którym uruchamiasz scrapery.
