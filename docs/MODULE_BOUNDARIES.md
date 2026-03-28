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
- emitują `DeprecationWarning` przez wspólny helper `scrapers.base.deprecated_entrypoint.run_deprecated_entrypoint`,
- przekierowują uruchomienie do `python -m scrapers.cli run <module>` (rejestr i dispatch są utrzymywane wyłącznie w `scrapers/cli.py`).

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

To jest stabilny punkt startowy dla integracji kodowych. Dla uruchomień operatorskich rekomendowana ścieżka to wyłącznie `python -m scrapers.cli ...`.

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

### 7.1 Harmonogram deprecacji (2 wersje przejściowe)

- **R0 (aktualna wersja):** legacy moduły działają, ale emitują `DeprecationWarning`.
- **R1 (kolejna wersja):** legacy moduły nadal działają, warning pozostaje obowiązkowy.
- **R2 (druga wersja przejściowa):** legacy moduły są usuwane.

Runtime warning ma teraz jawny komunikat o oknie migracji:
- `scheduled for removal after 2 transitional releases`
- oraz wskazanie canonical komendy `python -m scrapers.cli run <new_module>`.

### 7.2 Deprecated moduły i zamienniki (CLI/API)

#### Domenowe list-entrypointy (preferowane nowe API)

- `scrapers.circuits.list_scraper` -> `scrapers.circuits.entrypoint`
- `scrapers.constructors.current_constructors_list` -> `scrapers.constructors.entrypoint`
- `scrapers.drivers.list_scraper` -> `scrapers.drivers.entrypoint`
- `scrapers.grands_prix.list_scraper` -> `scrapers.grands_prix.entrypoint`
- `scrapers.seasons.list_scraper` -> `scrapers.seasons.entrypoint`

W praktyce oznacza to migrację:
- z `python -m scrapers.cli run scrapers.<domain>.list_scraper`
- na `python -m scrapers.cli run scrapers.<domain>.entrypoint`

#### Pozostałe legacy moduły (bez nowego modułu API, canonical przez `scrapers.cli run`)

- `scrapers.circuits.complete_scraper`
- `scrapers.constructors.former_constructors_list`
- `scrapers.constructors.indianapolis_only_constructors_list`
- `scrapers.constructors.privateer_teams_list`
- `scrapers.constructors.complete_scraper`
- `scrapers.drivers.female_drivers_list`
- `scrapers.drivers.fatalities_list_scraper`
- `scrapers.drivers.complete_scraper`
- `scrapers.engines.engine_manufacturers_list`
- `scrapers.engines.indianapolis_only_engine_manufacturers_list`
- `scrapers.engines.engine_regulation`
- `scrapers.engines.engine_restrictions`
- `scrapers.engines.complete_scraper`
- `scrapers.grands_prix.complete_scraper`
- `scrapers.grands_prix.red_flagged_races_scraper.non_championship`
- `scrapers.grands_prix.red_flagged_races_scraper.world_championship`
- `scrapers.seasons.complete_scraper`
- `scrapers.sponsorship_liveries.scraper`
- `scrapers.tyres.list_scraper`

### Mapa `old_command -> new_command`

- `python main.py --mode <layer0|layer1|full>` -> `python -m scrapers.cli wiki --mode <layer0|layer1|full>`
- `python -m scrapers.circuits.list_scraper` -> `python -m scrapers.cli run scrapers.circuits.entrypoint`
- `python -m scrapers.circuits.complete_scraper` -> `python -m scrapers.cli run scrapers.circuits.complete_scraper`
- `python -m scrapers.constructors.current_constructors_list` -> `python -m scrapers.cli run scrapers.constructors.entrypoint`
- `python -m scrapers.constructors.former_constructors_list` -> `python -m scrapers.cli run scrapers.constructors.former_constructors_list`
- `python -m scrapers.constructors.indianapolis_only_constructors_list` -> `python -m scrapers.cli run scrapers.constructors.indianapolis_only_constructors_list`
- `python -m scrapers.constructors.privateer_teams_list` -> `python -m scrapers.cli run scrapers.constructors.privateer_teams_list`
- `python -m scrapers.constructors.complete_scraper` -> `python -m scrapers.cli run scrapers.constructors.complete_scraper`
- `python -m scrapers.drivers.list_scraper` -> `python -m scrapers.cli run scrapers.drivers.entrypoint`
- `python -m scrapers.drivers.female_drivers_list` -> `python -m scrapers.cli run scrapers.drivers.female_drivers_list`
- `python -m scrapers.drivers.fatalities_list_scraper` -> `python -m scrapers.cli run scrapers.drivers.fatalities_list_scraper`
- `python -m scrapers.drivers.complete_scraper` -> `python -m scrapers.cli run scrapers.drivers.complete_scraper`
- `python -m scrapers.engines.engine_manufacturers_list` -> `python -m scrapers.cli run scrapers.engines.engine_manufacturers_list`
- `python -m scrapers.engines.indianapolis_only_engine_manufacturers_list` -> `python -m scrapers.cli run scrapers.engines.indianapolis_only_engine_manufacturers_list`
- `python -m scrapers.engines.engine_regulation` -> `python -m scrapers.cli run scrapers.engines.engine_regulation`
- `python -m scrapers.engines.engine_restrictions` -> `python -m scrapers.cli run scrapers.engines.engine_restrictions`
- `python -m scrapers.engines.complete_scraper` -> `python -m scrapers.cli run scrapers.engines.complete_scraper`
- `python -m scrapers.grands_prix.list_scraper` -> `python -m scrapers.cli run scrapers.grands_prix.entrypoint`
- `python -m scrapers.grands_prix.complete_scraper` -> `python -m scrapers.cli run scrapers.grands_prix.complete_scraper`
- `python -m scrapers.grands_prix.red_flagged_races_scraper.non_championship` -> `python -m scrapers.cli run scrapers.grands_prix.red_flagged_races_scraper.non_championship`
- `python -m scrapers.grands_prix.red_flagged_races_scraper.world_championship` -> `python -m scrapers.cli run scrapers.grands_prix.red_flagged_races_scraper.world_championship`
- `python -m scrapers.points.sprint_qualifying_points` -> `python -m scrapers.cli run scrapers.points.sprint_qualifying_points`
- `python -m scrapers.points.points_scoring_systems_history` -> `python -m scrapers.cli run scrapers.points.points_scoring_systems_history`
- `python -m scrapers.points.shortened_race_points` -> `python -m scrapers.cli run scrapers.points.shortened_race_points`
- `python -m scrapers.seasons.list_scraper` -> `python -m scrapers.cli run scrapers.seasons.entrypoint`
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

## 8. Static quality gates (CI)

Dla PR/push do `main` działa workflow `.github/workflows/static-quality-gates.yml` z czterema bramkami:

1. **Complexity warning (radon)** – próg ostrzegawczy: od klasy złożoności `B` wzwyż (`radon cc --min B`, krok typu warning).
2. **Complexity error (xenon)** – progi blokujące merge:
   - `--max-absolute C`
   - `--max-modules C`
   - `--max-average B`
3. **Duplicate code + oversized classes/functions (pylint)** – blokada CI przy wykryciu:
   - duplikacji (`duplicate-code`, `min-similarity-lines=30`),
   - zbyt dużych klas/funkcji (`too-many-*`) z limitami:
     - `max-attributes=20`
     - `max-public-methods=20`
     - `max-branches=15`
     - `max-statements=60`
4. **Reguły architektoniczne (import-linter)** – kontrakty zakazujące importów:
   - `models|validation -> infrastructure`
   - `models|validation|layers -> scrapers`

Konfiguracja bramek znajduje się w plikach:
- `.pylintrc`
- `importlinter.ini`
- `.github/workflows/static-quality-gates.yml`

## 9. Standard deklaracji konfiguracji scraperów (build_scraper_config + schema DSL)

Ujednolicamy jeden standard dla deklaracji `CONFIG` w scraperach tabelowych:

- `CONFIG` budujemy przez `build_scraper_config(...)`.
- Schemat deklarujemy przez DSL (`column(...)` + `TableSchemaDSL(...)`) albo przez helper zwracający schema DSL.
- Nie deklarujemy już ręcznie `CONFIG = ScraperConfig(...)` na poziomie klasy.
- Nie używamy aliasu `build_scraper_config` z `scrapers.base.table.builders` (deprecated).

### Moduły zmanualizowane wcześniej (`CONFIG = ScraperConfig(...)`) i zmigrowane do standardu

- `scrapers/drivers/female_drivers_list.py`
- `scrapers/drivers/fatalities_list_scraper.py`
- `scrapers/engines/engine_regulation.py`
- `scrapers/engines/engine_restrictions.py`
- `scrapers/grands_prix/red_flagged_races_scraper/non_championship.py`
- `scrapers/grands_prix/red_flagged_races_scraper/world_championship.py`
- `scrapers/points/sprint_qualifying_points.py`
- `scrapers/points/shortened_race_points.py`
- `scrapers/points/points_scoring_systems_history.py`
- `scrapers/tyres/list_scraper.py`
- `scrapers/base/helpers/tables/lap_records.py`

Dodatkowo import `build_scraper_config` został ujednolicony do canonical path (`scrapers.base.table.config`) także w modułach używających wcześniej aliasu z `builders`.

### Wymuszenie review/CI

Nowa reguła CI (`tests/test_scraper_config_ci_meta.py`) blokuje merge gdy:

- nowy scraper deklaruje klasowe `CONFIG = ScraperConfig(...)` zamiast `build_scraper_config(...)`,
- nowy scraper importuje `build_scraper_config` z deprecated aliasu `scrapers.base.table.builders`.


## 9. Rejestr decyzji architektonicznych (ADR)

Źródłem prawdy dla zatwierdzonych zasad architektonicznych jest katalog `docs/adr/`.

### Obowiązkowe ADR dla kluczowych kontraktów

- `ADR-0001` — kontrakt konfiguracji scraperów.
- `ADR-0002` — kontrakt parserów sekcji.
- `ADR-0003` — strategia Dependency Injection.
- `ADR-0004` — zasady nazewnictwa hooków.

### Wymóg powiązania zmian z ADR

Każda większa zmiana architektoniczna w PR musi:
- wskazywać numer ADR (`ADR-XXXX`) w opisie PR i/lub commit message,
- wskazywać, czy zmiana **stosuje** istniejącą decyzję, czy ją **modyfikuje**.

### Wymóg review

Jeżeli PR zmienia wcześniej zatwierdzoną zasadę, review wymaga:
- aktualizacji istniejącego ADR (zmiana statusu/konsekwencji), **lub**
- dodania nowego ADR, który zastępuje poprzedni (`Superseded by`).

Brak aktualizacji ADR w takim przypadku jest blockerem review.

## 10. Szablon „new scraper” (gotowy przykład DSL: lista + sekcja)

```python
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types import IntColumn, UrlColumn, AutoColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL

# --- wariant list scraper (SeedListTableScraper/F1TableScraper) ---
schema_columns = [
    column("Season", "season", UrlColumn()),
    column("Races", "races", IntColumn()),
    column("Notes", "notes", AutoColumn()),
]

CONFIG = build_scraper_config(
    url="https://en.wikipedia.org/wiki/Example",
    section_id="Example_section",
    expected_headers=["Season", "Races"],
    schema=TableSchemaDSL(columns=schema_columns),
    record_factory=record_from_mapping,
)

# --- wariant parsera sekcji (lokalna konfiguracja parse_table) ---
section_schema = TableSchemaDSL(
    columns=[
        column("Grand Prix", "grand_prix", UrlColumn()),
        column("Winner", "winner", AutoColumn()),
    ]
)

section_config = build_scraper_config(
    url="https://en.wikipedia.org/wiki/Example_section",
    expected_headers=["Grand Prix", "Winner"],
    schema=section_schema,
    record_factory=record_from_mapping,
)
```
