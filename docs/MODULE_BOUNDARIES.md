# Granice modułów parserów wiki (docelowy layout domen + entrypoint)

## 1. Finalny layout domenowy

Każda domena (`drivers`, `constructors`, `circuits`, `seasons`, `grands_prix`) ma ten sam szkielet:

- `entrypoint.py` — **jedyny wspierany entrypoint domenowy** (`run_list_scraper`).
- `list/` — seed scrape (lista encji i linków do szczegółów).
- `sections/` — parsowanie sekcji artykułu (`bodyContent`) i mapowanie tabel/treści.
- `infobox/` — mapowanie pól strukturalnych (`table.infobox`).
- `postprocess/` — normalizacja końcowa i domknięcie kontraktu danych.

Legacy pliki typu `list_scraper.py` / `*_constructors_list.py` pozostają tylko jako zgodność wsteczna:
- mają oznaczenie **deprecated**,
- emitują `DeprecationWarning`,
- delegują uruchomienie do `entrypoint.py`.

## 2. Reguły zależności między warstwami

- `list/` nie importuje `sections/`, `infobox/`, `postprocess/`.
- `sections/` nie importuje `single_scraper.py` ani legacy `list_scraper.py`.
- `infobox/` nie importuje `list/`, `sections/`, `postprocess/`.
- `postprocess/` nie importuje `list/`, `sections/`, `infobox/`.

Warstwy komunikują się przez kontrakty i orchestration w scraperach domenowych, nie przez ciasne importy między katalogami warstw.

## 3. Standardowy interfejs uruchamiania

Każda domena eksportuje z `entrypoint.py` funkcję:

- `run_list_scraper(*, run_config: RunConfig | None = None) -> None`

To jest docelowy punkt startowy dla CLI/skryptów i automatyzacji.

## 4. Przykładowy flow per domena

### `drivers`
1. `scrapers.drivers.entrypoint.run_list_scraper()`
2. `drivers/list_scraper.py` (klasa listy + parser tabeli)
3. `drivers/sections/*` + `drivers/infobox/*` w scraperach szczegółowych
4. `drivers/postprocess/*` (normalizacja końcowa)

### `constructors`
1. `scrapers.constructors.entrypoint.run_list_scraper()`
2. `constructors/current_constructors_list.py` (lista bieżącego sezonu)
3. `constructors/sections/*` + `constructors/infobox/*`
4. `constructors/postprocess/*`

### `circuits`
1. `scrapers.circuits.entrypoint.run_list_scraper()`
2. `circuits/list_scraper.py`
3. `circuits/sections/*` + `circuits/infobox/*`
4. `circuits/postprocess/*`

### `seasons`
1. `scrapers.seasons.entrypoint.run_list_scraper()`
2. `seasons/list_scraper.py`
3. `seasons/sections/*` + `seasons/infobox/*`
4. `seasons/postprocess/*`

### `grands_prix`
1. `scrapers.grands_prix.entrypoint.run_list_scraper()`
2. `grands_prix/list_scraper.py`
3. `grands_prix/sections/*` + `grands_prix/infobox/*`
4. `grands_prix/postprocess/*`

## 5. Kontrola statyczna

W repo jest test statyczny sprawdzający:
- obecność `entrypoint.py` i wymaganych katalogów warstw w każdej domenie,
- brak zabronionych importów łamiących granice architektoniczne.
