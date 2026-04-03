# Granice modułów parserów wiki (docelowy layout domen + entrypoint)

## 1. Finalny layout domenowy

Każda domena (`drivers`, `constructors`, `circuits`, `seasons`, `grands_prix`) ma ten sam szkielet:

- `entrypoint.py` — **jedyny wspierany entrypoint domenowy** (`run_list_scraper`).
- `list/` — seed scrape (lista encji i linków do szczegółów).
- `sections/` — parsowanie sekcji artykułu (`bodyContent`) i mapowanie tabel/treści.
- `infobox/` — mapowanie pól strukturalnych (`table.infobox`).
- `services/` — usługi domenowe i orkiestracja pomocnicza (np. składanie rekordów).
- `postprocess/` — normalizacja końcowa i domknięcie kontraktu danych.
- `validators.py` — opcjonalny punkt walidacji domenowej (lub `validator.py` tylko przejściowo).

Pliki typu `list_scraper.py` / `*_constructors_list.py` traktujemy jako finalne moduły domenowe.
Nie utrzymujemy dla nich warstwy kompatybilności wstecznej (bez aliasów legacy, bez `DeprecationWarning`, bez migracyjnych wrapperów CLI).

### 1.0 Mapa odpowiedzialności kluczowych katalogów

| Katalog | Odpowiedzialność (skrót) | Entrypoint(y) | Właściciel logiczny | Granice użycia |
|---|---|---|---|---|
| `scrapers/cli.py` | Canonical launcher i dispatch uruchomień scraperów. | `python -m scrapers.cli ...` | Platforma scraperów (warstwa orkiestracji) | Nie umieszczamy logiki domenowej; tylko routing i konfiguracja run (bez warstwy legacy/migracyjnej). |
| `scrapers/base/` | Wspólne kontrakty, adaptery, helpery i abstrakcje wielodomenowe. | Importowane API bazowe (`scrapers.base.*`) | Platforma scraperów (warstwa bazowa) | Bez wiedzy o konkretnych domenach (`drivers`, `circuits`, itd.); nowe API musi być generyczne i testowalne. |
| `scrapers/<domain>/entrypoint.py` | Stabilny punkt startowy domeny (`run_list_scraper`). | Run configuration w PyCharm | Właściciel domeny (`<domain>`) | Entrypoint orkiestruje flow i deleguje do warstw; nie duplikuje parserów/normalizacji. |
| `scrapers/<domain>/list/` lub `list_scraper.py` | Seed scrape: lista encji + linki do szczegółów. | `run_list_scraper()` przez entrypoint domeny | Właściciel domeny (`<domain>`) | Brak importów do `sections/`, `infobox/`, `postprocess/`; tylko etap listowania/seedów. |
| `scrapers/<domain>/sections/` | Parsowanie sekcji `bodyContent` i tabel artykułu. | Wywołania z `single_scraper.py` / serwisów domenowych | Właściciel domeny (`<domain>`) | Nie importuje `single_scraper.py` (zakaz zależności zwrotnej) ani legacy launcherów listowych. |
| `scrapers/<domain>/infobox/` | Parsowanie danych strukturalnych `table.infobox`. | Wywołania z flow domeny (`single_scraper`/services) | Właściciel domeny (`<domain>`) | Brak importów do `list/`, `sections/`, `postprocess/`; warstwa niezależna od pozostałych parserów. |
| `scrapers/<domain>/services/` | Usługi domenowe i składanie rekordów pośrednich/końcowych. | API usług domenowych (`scrapers.<domain>.services.*`) | Właściciel domeny (`<domain>`) | Łączy komponenty domeny bez łamania granic warstw i bez przenoszenia logiki do CLI/base. |
| `scrapers/<domain>/postprocess/` | Normalizacja końcowa i domknięcie kontraktu danych. | Etap końcowy flow domeny | Właściciel domeny (`<domain>`) | Brak importów do `list/`, `sections/`, `infobox/`; tylko końcowe porządki i walidacje. |

**Zasada utrzymania mapy:** przy każdej zmianie architektonicznej (nowe granice, nowy entrypoint, zmiana odpowiedzialności katalogu) aktualizujemy tabelę 1.0 w tym samym PR.

## 1.1 Mapa migracji nazw/ścieżek (standaryzacja `services/`)

W ramach refaktoru domenowego przeniesiono usługi składania rekordów do katalogów `services/`.
Faza przejściowa z aliasami importów została domknięta — aliasy usunięto po aktualizacji importów.

| Domena | Stara ścieżka | Nowa ścieżka |
|---|---|---|
| `circuits` | `scrapers.circuits.domain_record_service` | `scrapers.circuits.services.domain_record` |
| `constructors` | `scrapers.constructors.domain_record_service` | `scrapers.constructors.services.domain_record` |
| `drivers` | `scrapers.drivers.domain_record_service` | `scrapers.drivers.services.domain_record` |
| `seasons` | `scrapers.seasons.domain_record_service` | `scrapers.seasons.services.domain_record` |

## 2. Reguły zależności między warstwami

- `list/` nie importuje `sections/`, `infobox/`, `postprocess/`.
- `sections/` nie importuje `single_scraper.py` ani żadnych wrapperów uruchomieniowych.

## 2.1 Twarde reguły: brak kompatybilności wstecznej

- Nie dodajemy aliasów API/importów dla starych nazw.
- Nie dodajemy fallbacków danych (`legacy`, `compatible`, `migration`) w runtime.
- Nie emitujemy `DeprecationWarning` ani harmonogramów wygaszania.
- Gdy kontrakt się zmienia, aktualizujemy od razu wszystkie call-site’y i dokumentację.
- CLI wspiera tylko aktualne, canonical komendy.
- `infobox/` nie importuje `list/`, `sections/`, `postprocess/`.
- `postprocess/` nie importuje `list/`, `sections/`, `infobox/`.
- `single_scraper.py` może importować moduły z `sections/` (do orkiestracji parsowania).
- `sections/` nie może importować `single_scraper.py` (zakaz zależności zwrotnej).

Warstwy komunikują się przez kontrakty i orchestration w scraperach domenowych, nie przez ciasne importy między katalogami warstw.

### Aktualizacja po uproszczeniu abstrakcji (2026-04-02)

- Fabryki usług sekcji zostały uproszczone: per-domenowe klasy pass-through (`*SectionServiceFactory`) zastąpiono jedną konfigurującą fabryką bazową `ConfigurableSectionServiceFactory` w `scrapers/base/sections/factory.py`.
- Abstrakcję kontraktową `SectionServiceFactory` pozostawiono, bo realnie wspiera testowalność (podmiana zależności przez `for_tests(...)`) i zmienność implementacji.
- Usunięto przestarzały wrapper `SectionAdapter.parse_section_dicts(...)`; granica serializacji sekcji jest teraz jednoznaczna: `SectionAdapter.assemble_section_dicts(...)`.

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

To jest stabilny punkt startowy dla integracji kodowych. Dla uruchomień operatorskich jedyną wspieraną ścieżką jest konfiguracja Run w PyCharm.

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

### 6.1 Checklista PR (obowiązkowa dla zmian scraperów)

Każdy PR obejmujący kod scraperów przechodzi przez poniższą checklistę architektoniczną:

- [ ] **SRP (Single Responsibility Principle):** nowe/zmienione klasy i moduły mają pojedynczą odpowiedzialność.
- [ ] **Brak duplikacji logiki:** logika nie jest kopiowana pomiędzy domenami i modułami.
- [ ] **Użycie wspólnych abstrakcji:** preferowane są istniejące komponenty bazowe (`scrapers/base/*`) lub rozszerzenie wspólnego API.
- [ ] **Brak nowych `Any` w domenie:** nowe adnotacje typów w kodzie domenowym nie wprowadzają kolejnych `Any` (chyba że istnieje formalnie udokumentowany wyjątek techniczny).
- [ ] **Zgodność z extension guide:** nowy scraper spełnia kontrakt i antywzorce opisane w `docs/architecture/scraper-extension-guide.md`.
- [ ] **Zgodność zmian z mapą odpowiedzialności (sekcja 1.0):** granice użycia, właściciel logiczny i entrypointy pozostały spójne albo zostały jawnie zaktualizowane.
- [ ] **Aktualizacja mapy po zmianie architektonicznej:** jeżeli zmienia się odpowiedzialność katalogów, granice lub entrypointy, sekcja 1.0 została zaktualizowana w tym samym PR.
- [ ] **Debug Quickstart aktualny:** dla zmian architektonicznych zaktualizowano `docs/DEBUG_QUICKSTART.md` (lub uzasadniono brak zmian).

### 6.2 „Architecture impact” dla zmian w `scrapers/base/`

Jeżeli PR modyfikuje pliki pod `scrapers/base/`, opis PR **musi** zawierać sekcję:

`Architecture impact`:
- co zostało zmienione w warstwie bazowej,
- które domeny (`drivers`, `constructors`, `circuits`, `seasons`, `grands_prix`, inne) są dotknięte,
- czy zmiana jest kompatybilna wstecz,
- czy wymagane są działania migracyjne.

Brak sekcji `Architecture impact` dla zmian w `scrapers/base/` traktujemy jako niekompletny PR.

### 6.3 Reguła implementacji nowej funkcjonalności

Nowa funkcjonalność powinna być projektowana w następującej kolejności:

1. **Najpierw** sprawdzić możliwość osadzenia jej we wspólnych komponentach bazowych (kontrakty, helpery, parsery, DSL, adaptery).
2. Jeżeli krok 1 nie jest zasadny (np. przypadek specyficzny dla jednej domeny), dopiero wtedy tworzyć implementację lokalną.
3. Decyzję o lokalnej implementacji należy uzasadnić w opisie PR (krótka notatka dlaczego nie użyto/nie rozszerzono warstwy bazowej).

### 6.4 Przegląd „duplikacja tygodnia” (rytuał sprintowy)

Minimum raz na sprint wykonujemy krótki przegląd duplikacji (`duplikacja tygodnia`):

- identyfikujemy 1–3 najwyżej priorytetowe duplikacje logiki,
- tworzymy zadania porządkowe (cleanup/refactor) w backlogu,
- przypisujemy orientacyjny termin domknięcia (najlepiej w tym samym lub kolejnym sprincie).


## 7. Mapa kompatybilności legacy CLI

CLI (`python -m ...`, w tym `python -m scrapers.cli`) pozostaje wyłącznie mechanizmem kompatybilności i nie jest wspieranym sposobem uruchamiania projektu.

### 7.1 Harmonogram deprecacji (2 wersje przejściowe)

<!-- generated-from: scrapers.cli.render_deprecation_schedule_markdown -->
- **R0 (aktualna wersja):** legacy moduły działają, ale emitują `DeprecationWarning`.
- **R1 (kolejna wersja):** legacy moduły nadal działają, warning pozostaje obowiązkowy.
- **R2 (druga wersja przejściowa):** legacy moduły są usuwane.

Runtime warning ma teraz jawny komunikat o oknie migracji:
- `scheduled for removal after 2 transitional releases (removal target: R2)`
- oraz wskazanie modułu docelowego uruchamianego przez konfigurację Run w PyCharm.

<!-- BEGIN AUTO-GENERATED: command-migration-map -->

### 7.2 Canonical command map (CLI/API)

Repo nie utrzymuje już warstwy kompatybilności wstecznej ani deprecated-wrapperów.

W praktyce oznacza to migrację:
- z `python -m scrapers.<domain>.list_scraper`
- na `python -m scrapers.<domain>.entrypoint`

- `python main.py` -> `from scrapers import run_wiki_flow; run_wiki_flow()`
- `python -m scrapers.circuits.complete_scraper` -> `python -m scrapers.circuits.complete_scraper`
- `python -m scrapers.circuits.list_scraper` -> `python -m scrapers.circuits.entrypoint`
- `python -m scrapers.constructors.complete_scraper` -> `python -m scrapers.constructors.complete_scraper`
- `python -m scrapers.constructors.current_constructors_list` -> `python -m scrapers.constructors.entrypoint`
- `python -m scrapers.constructors.former_constructors_list` -> `python -m scrapers.constructors.former_constructors_list`
- `python -m scrapers.constructors.indianapolis_only_constructors_list` -> `python -m scrapers.constructors.indianapolis_only_constructors_list`
- `python -m scrapers.constructors.privateer_teams_list` -> `python -m scrapers.constructors.privateer_teams_list`
- `python -m scrapers.drivers.complete_scraper` -> `python -m scrapers.drivers.complete_scraper`
- `python -m scrapers.drivers.fatalities_list_scraper` -> `python -m scrapers.drivers.fatalities_list_scraper`
- `python -m scrapers.drivers.female_drivers_list` -> `python -m scrapers.drivers.female_drivers_list`
- `python -m scrapers.drivers.list_scraper` -> `python -m scrapers.drivers.entrypoint`
- `python -m scrapers.engines.complete_scraper` -> `python -m scrapers.engines.complete_scraper`
- `python -m scrapers.engines.engine_manufacturers_list` -> `python -m scrapers.engines.engine_manufacturers_list`
- `python -m scrapers.engines.engine_regulation` -> `python -m scrapers.engines.engine_regulation`
- `python -m scrapers.engines.engine_restrictions` -> `python -m scrapers.engines.engine_restrictions`
- `python -m scrapers.engines.indianapolis_only_engine_manufacturers_list` -> `python -m scrapers.engines.indianapolis_only_engine_manufacturers_list`
- `python -m scrapers.grands_prix.complete_scraper` -> `python -m scrapers.grands_prix.complete_scraper`
- `python -m scrapers.grands_prix.list_scraper` -> `python -m scrapers.grands_prix.entrypoint`
- `python -m scrapers.grands_prix.red_flagged_races_scraper.world_championship` -> `python -m scrapers.grands_prix.red_flagged_races_scraper.world_championship`
- `python -m scrapers.points.points_scoring_systems_history` -> `python -m scrapers.points.points_scoring_systems_history`
- `python -m scrapers.points.shortened_race_points` -> `python -m scrapers.points.shortened_race_points`
- `python -m scrapers.points.sprint_qualifying_points` -> `python -m scrapers.points.sprint_qualifying_points`
- `python -m scrapers.seasons.complete_scraper` -> `python -m scrapers.seasons.complete_scraper`
- `python -m scrapers.seasons.list_scraper` -> `python -m scrapers.seasons.entrypoint`
- `python -m scrapers.sponsorship_liveries.scraper` -> `python -m scrapers.sponsorship_liveries.scraper`
- `python -m scrapers.tyres.list_scraper` -> `python -m scrapers.tyres.list_scraper`

<!-- END AUTO-GENERATED: command-migration-map -->

## 3.1 Rules / Uruchamianie projektu

- **Twarda reguła:** jedyny wspierany sposób uruchamiania projektu to konfiguracja **Run** w **PyCharm**.
- Uruchamianie z terminala (`python -m ...`, w tym `python -m scrapers.cli ...`) jest **niewspierane**.
- Wszystkie przykłady komend CLI w tym dokumencie mają charakter historyczny/kompatybilnościowy i nie stanowią rekomendacji operacyjnej.

## ✅ Krótka checklista: jak tworzyć nowy scraper listowy

1. Dziedzicz po `SeedListTableScraper` i ustaw `domain`, `default_output_path`, `legacy_output_path`.
2. Zdefiniuj schemat kolumn (`build_columns(...)`) albo `schema=...`.
3. Buduj `CONFIG` wyłącznie przez `scrapers.base.table.config.build_scraper_config(...)`.
4. Ustaw minimalne `expected_headers` (podzbiór wymaganych nagłówków tabeli).
5. Podepnij `record_factory` i (opcjonalnie) `default_validator`.
6. Dla uruchamiania używaj konfiguracji Run w PyCharm wskazującej `entrypoint.py`; `list_scraper.py` traktuj jako warstwę kompatybilności.

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

### 8.1 Mapowanie reguł checklisty PR -> automatyczne bramki

Dokumentacja pozostaje opisowa, ale egzekucja reguł jest realizowana przez automatyczne bramki CI.

| Reguła z checklisty PR | Automated check (źródło egzekucji) |
|---|---|
| Brak nowych `Any` | `Strict typing regression gate (mypy)` w `.github/workflows/static-quality-gates.yml` (`scripts/ci/mypy_regression_gate.py`) |
| Granice modułów | `Architecture tests` (`tests/test_architecture_import_rules.py`, `tests/test_section_architecture_boundaries.py`) + `import-linter` (`lint-imports --config importlinter.ini`) |
| Duplikacja | `Scan changed Python files for duplicate fragments (jscpd)` + `Duplicate code and oversized units gate (pylint)` |
| Architecture impact | Walidator PR template: `scripts/ci/validate_pr_template.py` + wymagane pola w `.github/pull_request_template.md` |

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

### CI gate: automatyczna walidacja referencji ADR

Workflow `static-quality-gates.yml` uruchamia skrypt `scripts/ci/enforce_architecture_adr_reference.py`, który:
- analizuje diff i wykrywa zmiany w ścieżkach: `layers/`, `scrapers/base/`, `tests/architecture/`,
- wymaga co najmniej jednej referencji `ADR-XXXX` w tytule/opisie PR lub commit message,
- ignoruje zmiany wyłącznie kosmetyczne (puste linie, formatowanie, komentarze `#`).

### Przykłady poprawnych referencji

- `ADR-0002: dostosowanie parsera sekcji do nowego kontraktu`
- `Implement cache boundary for layer adapters (ADR-0003)`
- `Refactor hook names according to ADR-0004`

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


## 9. Canonical package entrypoints (API vs internal)

Dla pakietów technicznych (`layers`, `scrapers.base`, `models`) obowiązuje jawny podział:

- **`layers`**
  - canonical API: `layers.create_default_wiki_pipeline_application`
  - internal: `layers.zero.*`, `layers.one.*`, `layers.orchestration.*`, helpery/fabryki
- **`models`**
  - canonical API: `models.services.parse_seasons`, `models.value_objects.{EntityName, SeasonYear, SectionId, WikiUrl}`
  - internal: pozostałe moduły `models.*` importowane bezpośrednio tylko gdy brak publicznego aliasu
- **`scrapers.base`**
  - canonical API: wyspecjalizowane subpackage API (`scrapers.base.constants`, `scrapers.base.table.columns.types`, `scrapers.base.orchestration.components`)
  - internal: `scrapers.base.services` oraz pozostałe moduły implementacyjne bez stabilnej gwarancji API

Zasada YAGNI: nowy eksport w `__init__.py` dodajemy wyłącznie po potwierdzeniu realnego użycia poza pakietem.
