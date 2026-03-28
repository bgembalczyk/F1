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
- `single_scraper.py` może importować moduły z `sections/` (do orkiestracji parsowania).
- `sections/` nie może importować `single_scraper.py` (zakaz zależności zwrotnej).

Warstwy komunikują się przez kontrakty i orchestration w scraperach domenowych, nie przez ciasne importy między katalogami warstw.

### Niedozwolone kierunki importu

- `sections/ -> single_scraper.py`
- `list/ -> sections/`
- `list/ -> infobox/`
- `list/ -> postprocess/`
- `infobox/ -> list/`
- `infobox/ -> sections/`
- `infobox/ -> postprocess/`
- `postprocess/ -> list/`
- `postprocess/ -> sections/`
- `postprocess/ -> infobox/`

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


## 6. Standard DoD merge-gate dla parserów sekcji

Każdy PR, który dodaje lub modyfikuje plik w `scrapers/*/sections/`, musi spełnić pełny merge-gate:

- Snapshot HTML (`minimal + edge`) dla domen parserów sekcji.
- Aliasy sekcji (regresje mapowania nagłówków i fallbacków).
- Test kontraktu (`SectionParseResult` + metadata parsera).
- Wpis w dokumentacji domeny (`scrapers/<domain>/README.md`) o zakresie zmiany parsera.

Wymuszenie CI:
- test meta (`tests/test_section_parser_ci_meta.py`) blokuje merge, gdy pojawi się nowy moduł `scrapers/*/sections/*.py` bez rozszerzenia macierzy snapshot/contract.

Checklistę operacyjną merge-gate utrzymujemy również w `docs/CHANGES_CHECKLIST.md`.


## 7. Canonical launcher CLI i mapa kompatybilności

Jedynym canonical launcherem jest teraz `python -m scrapers.cli`.

### Mapa `old_command -> new_command`

- `python main.py --mode <layer0|layer1|full>` -> `python -m scrapers.cli wiki --mode <layer0|layer1|full>`
- `python -m scrapers.circuits.list_scraper` -> `python -m scrapers.cli run scrapers.circuits.list_scraper`
- `python -m scrapers.circuits.complete_scraper` -> `python -m scrapers.cli run scrapers.circuits.complete_scraper`
- `python -m scrapers.constructors.current_constructors_list` -> `python -m scrapers.cli run scrapers.constructors.current_constructors_list`
- `python -m scrapers.constructors.former_constructors_list` -> `python -m scrapers.cli run scrapers.constructors.former_constructors_list`
- `python -m scrapers.constructors.indianapolis_only_constructors_list` -> `python -m scrapers.cli run scrapers.constructors.indianapolis_only_constructors_list`
- `python -m scrapers.constructors.privateer_teams_list` -> `python -m scrapers.cli run scrapers.constructors.privateer_teams_list`
- `python -m scrapers.constructors.complete_scraper` -> `python -m scrapers.cli run scrapers.constructors.complete_scraper`
- `python -m scrapers.drivers.list_scraper` -> `python -m scrapers.cli run scrapers.drivers.list_scraper`
- `python -m scrapers.drivers.female_drivers_list` -> `python -m scrapers.cli run scrapers.drivers.female_drivers_list`
- `python -m scrapers.drivers.fatalities_list_scraper` -> `python -m scrapers.cli run scrapers.drivers.fatalities_list_scraper`
- `python -m scrapers.drivers.complete_scraper` -> `python -m scrapers.cli run scrapers.drivers.complete_scraper`
- `python -m scrapers.engines.engine_manufacturers_list` -> `python -m scrapers.cli run scrapers.engines.engine_manufacturers_list`
- `python -m scrapers.engines.indianapolis_only_engine_manufacturers_list` -> `python -m scrapers.cli run scrapers.engines.indianapolis_only_engine_manufacturers_list`
- `python -m scrapers.engines.engine_regulation` -> `python -m scrapers.cli run scrapers.engines.engine_regulation`
- `python -m scrapers.engines.engine_restrictions` -> `python -m scrapers.cli run scrapers.engines.engine_restrictions`
- `python -m scrapers.engines.complete_scraper` -> `python -m scrapers.cli run scrapers.engines.complete_scraper`
- `python -m scrapers.grands_prix.list_scraper` -> `python -m scrapers.cli run scrapers.grands_prix.list_scraper`
- `python -m scrapers.grands_prix.complete_scraper` -> `python -m scrapers.cli run scrapers.grands_prix.complete_scraper`
- `python -m scrapers.grands_prix.red_flagged_races_scraper.non_championship` -> `python -m scrapers.cli run scrapers.grands_prix.red_flagged_races_scraper.non_championship`
- `python -m scrapers.grands_prix.red_flagged_races_scraper.world_championship` -> `python -m scrapers.cli run scrapers.grands_prix.red_flagged_races_scraper.world_championship`
- `python -m scrapers.points.sprint_qualifying_points` -> `python -m scrapers.cli run scrapers.points.sprint_qualifying_points`
- `python -m scrapers.points.points_scoring_systems_history` -> `python -m scrapers.cli run scrapers.points.points_scoring_systems_history`
- `python -m scrapers.points.shortened_race_points` -> `python -m scrapers.cli run scrapers.points.shortened_race_points`
- `python -m scrapers.seasons.list_scraper` -> `python -m scrapers.cli run scrapers.seasons.list_scraper`
- `python -m scrapers.seasons.complete_scraper` -> `python -m scrapers.cli run scrapers.seasons.complete_scraper`
- `python -m scrapers.sponsorship_liveries.scraper` -> `python -m scrapers.cli run scrapers.sponsorship_liveries.scraper`
- `python -m scrapers.tyres.list_scraper` -> `python -m scrapers.cli run scrapers.tyres.list_scraper`

Każdy wrapper legacy emituje `DeprecationWarning` z powyższym mapowaniem.

## ✅ Krótka checklista: jak tworzyć nowy scraper listowy

1. Dziedzicz po `SeedListTableScraper` i ustaw `domain`, `default_output_path`, `legacy_output_path`.
2. Zdefiniuj schemat kolumn (`build_columns(...)`) albo `schema=...`.
3. Buduj `CONFIG` wyłącznie przez `scrapers.base.table.config.build_scraper_config(...)`.
4. Ustaw minimalne `expected_headers` (podzbiór wymaganych nagłówków tabeli).
5. Podepnij `record_factory` i (opcjonalnie) `default_validator`.
6. Dla uruchamiania używaj `entrypoint.py`; `list_scraper.py` traktuj jako warstwę kompatybilności.
