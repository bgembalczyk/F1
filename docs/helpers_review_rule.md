# Reguła review: brak nowych funkcji w ogólnych `helpers.py`

## Zasada

Nowe funkcje **nie mogą** być dodawane do ogólnych plików `helpers.py`.

## Jak postępować

1. Dodaj funkcję do modułu nazwanego po celu (np. `path_resolution.py`, `record_merging.py`, `source_mapping.py`).
2. Jeśli istniejące `helpers.py` działa jako shim, można jedynie dopisać re-export nowej funkcji (bez implementacji logiki).
3. W opisie PR wskaż nowy moduł docelowy i use-case.

## Wyjątki

Wyjątek wymaga uzasadnienia w PR w sekcji **"Uzasadnienie dla helpers.py"** i planu migracji do modułu celowego.
