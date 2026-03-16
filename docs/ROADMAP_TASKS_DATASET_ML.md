# Plan dojścia do docelowej architektury (taski)

> Ten plik jest źródłem prawdy przy zadaniach typu „zaplanuj kolejne taski”.
> Status aktualizujemy checkboxami: `[ ]` / `[x]`.

## Etap 1 — Fundament seed scraperów (Warstwa 0)
- [x] Zdefiniować listę stron startowych (kierowcy, konstruktorzy, GP, tory, sezony).
  - Potwierdzenie: istnieją dedykowane list scrape'ry dla kluczowych seedów (`drivers`, `constructors`, `grands_prix`, `circuits`, `seasons`).
  - Moduły referencyjne: `scrapers/drivers/list_scraper.py`, `scrapers/constructors/*_list*.py`, `scrapers/grands_prix/list_scraper.py`, `scrapers/circuits/list_scraper.py`, `scrapers/seasons/list_scraper.py`.
- [x] Dodać konfigurację mapującą: `seed_name -> wikipedia_url -> output_category`.
  - Status migracji: centralny moduł ścieżek (`DataPaths`) oraz rejestr seedów/list jobów został rozszerzony o ścieżki docelowe (`data/raw/...`) i legacy (`data/wiki/...`) do bezpiecznej migracji.
- [ ] Ustalić minimalny wspólny schemat rekordu seed (`name`, `link`, `source_url`, `scraped_at`).
- [x] Wdrożyć eksport JSON dla każdej kategorii do `data/raw/<category>/`.
  - Status migracji: writer seed L0 wspiera bezpośredni zapis przez `DataPaths` do `data/raw/<category>/...`.
- [ ] Dodać logowanie jakości: liczba rekordów, puste pola, duplikaty.

## Etap 2 — Parsery encji szczegółowych (Warstwa 1)
- [ ] Dodać parser infoboxów dla stron encji (driver/constructor/circuit/grand_prix/season).
  - Status: częściowo zrobione dla `driver`/`constructor`/`circuit`; brak spójnego domknięcia dla całego kompletu encji 1:1 z roadmapą.
- [ ] Znormalizować kluczowe pola (daty, kraj, aliasy nazw).
- [ ] Dodać mapowanie i wersjonowanie schematów rekordów.
- [ ] Zapisywać wynik w `data/normalized/<category>/`.

## Etap 3 — Iteracyjny orchestrator 0/1 (na sztywno)
- [ ] Zaimplementować orchestrator kroków z ręcznie określonym zakresem przejść 0/1.
- [ ] Dla każdego kroku jawnie wskazać źródło kolejnych punktów startowych (`checkpoint_input`).
- [ ] Dodać rejestr kroków: `krok -> skąd wejście -> jaki parser -> gdzie wyjście`.
- [ ] Zapewnić, że nie scrapujemy ponownie danych już przetworzonych bez potrzeby.

## Etap 4 — Stabilność i obserwowalność pipeline
- [ ] Dodać metryki pipeline (czas, liczba rekordów, błędy parserów).
- [ ] Dodać raporty jakości po każdym kroku iteracji.
- [ ] Dodać testy parserów na snapshotach HTML.
- [x] Dodać retry/backoff dla fetchowania stron.
  - Potwierdzenie: opcje `http_retries` i `http_backoff_seconds` są częścią konfiguracji scrapera i HTTP klienta.
  - Moduły referencyjne: `scrapers/base/options.py`, `scrapers/base/run_config.py`, `infrastructure/http_client/config.py`.

## Etap 5 — Przygotowanie pod ML (później)
- [ ] Zdefiniować cechy i słowniki tokenizacji.
- [ ] Dodać etap kodowania cech do `data/ml_ready/`.
- [ ] Zbudować wersjonowane zestawy treningowe.

## Nowe zadania wynikające z aktualnych luk
- [x] Adapter sekcji: wprowadzić warstwę `SectionSourceAdapter` dla pobierania „kolejnych punktów startowych” bezpośrednio z `data/checkpoints/*.json` (z fallbackiem do `data/raw/*`).
  - Status migracji: dodany fallback kompatybilności do legacy ścieżek `data/wiki/<domain>/*.json`.
- [ ] Orchestrator 0/1: dodać jawny `StepOrchestrator` (hardcoded flow) wykonujący kroki `L0 -> L1 -> L0/L1` z deklaratywnym `checkpoint_input` i rejestrem kroków.
- [x] Migracja output layout: przejść z obecnego `data/wiki/...` na layout docelowy (`data/raw`, `data/normalized`, `data/checkpoints`) z mapą kompatybilności ścieżek i etapem migracyjnym.
  - Status migracji: dodano skrypt `scripts/migrate_data_layout.py` mapujący stare pliki do nowego layoutu oraz raportujący brakujące pliki/kolizje.

## Reguły wersjonowania i layout plików danych
- Struktura katalogów jest wersjonowana semantycznie przez layout (`v1`):
  - `data/raw/<domain>/list/*.json` — wyniki list/seed scraperów (warstwa surowa),
  - `data/normalized/<domain>/*.json` — rekordy po normalizacji,
  - `data/checkpoints/step_<id>_<layer>_<domain>.json` — checkpointy pipeline.
- Każda zmiana łamiąca kompatybilność nazewnictwa plików powinna:
  1. utrzymać fallback odczytu legacy co najmniej przez jeden cykl migracyjny,
  2. dodać mapowanie w skrypcie migracyjnym,
  3. zostać odnotowana w tej roadmapie jako status migracji.

## Następne 3 konkretne taski (short-term)
- [ ] Task A: Utworzyć konfigurację seed URL-i i kategorii wyjściowych.
  - Skąd bierzemy kolejne punkty startowe: wejście inicjalne z `data/wiki/drivers/f1_drivers.json` oraz `data/wiki/constructors/f1_former_constructors.json` jako bootstrap do pierwszego checkpointu (`data/checkpoints/step_0_layer0.json`).
- [ ] Task B: Ujednolicić format rekordu seed + writer JSON.
  - Skąd bierzemy kolejne punkty startowe: po standaryzacji zapis do `data/raw/<category>/...`; `checkpoint_input` następnego kroku wskazuje konkretny plik `data/raw/drivers/drivers_seed_v1.json`.
- [ ] Task C: Dodać pierwszy pionowy slice end-to-end dla `drivers` z checkpointem wejścia do kolejnego kroku.
  - Skąd bierzemy kolejne punkty startowe: `data/checkpoints/step_1_layer1_drivers.json` (URL-e kierowców po L0) -> wejście do kolejnego kroku L1.


## Etap 0.5 — Ujednolicenie struktury domen parserów (NOWE)
- [x] Dodać spójny podział katalogów domenowych: `list/`, `sections/`, `infobox/`, `postprocess/`.
- [x] Wydzielić logikę sekcyjną z parserów single/list do `sections/` (driver results, grand prix by year, season adapters: calendar/results/standings).
- [x] Wprowadzić wspólny interfejs parsera sekcyjnego (`SectionParseResult`, `SectionParser`).
- [x] Dodać mapę `DOMAIN_CRITICAL_SECTIONS` (`section_id`, `alternative_section_ids`) i użyć jej jako fallbacku w parserach GP.
- [ ] Migrować kolejne parsery domenowe (constructors/circuits) na nowy interfejs sekcyjny.

## Strumień C — Podział projektu na wcześniej powstałe części (stabilizacja architektury)
- [x] C1. Domknąć mapę odpowiedzialności modułów: `list/` (seed), `sections/` (body), `infobox/` (structured core), `postprocess/` (normalizacja domenowa).
  - Kontekst: dodano dokument granic modułów z mapą odpowiedzialności i regułami przepływu.
- [x] C2. Wymusić regułę importów: moduły `sections/` nie odwołują się do `single_scraper.py`; komunikacja wyłącznie przez serwisy/adaptory.
  - Kontekst: dodano test regresyjny skanujący importy we wszystkich domenach sekcyjnych.
- [x] C3. Dodać dokument „granice modułów” z przykładami przepływu danych dla każdej domeny (`drivers`, `constructors`, `circuits`, `seasons`, `grands_prix`).
  - Kontekst: nowy dokument `docs/MODULE_BOUNDARIES.md` z przykładami flow 0→1 i użyciem adaptera sekcji.
- [x] C4. Wprowadzić checklistę Definition of Done dla każdego nowego parsera sekcji (test snapshotowy + mapowanie aliasów + walidacja kontraktu + wpis w README domeny).
  - Kontekst: checklista DoD została osadzona w dokumencie granic modułów jako standard wejścia do code review, a testy sekcji korzystają ze wspólnego template'u fixture + expected records + metadata assertions.
- [x] C5. Przenieść wspólne helpery czyszczenia treści wiki do jednego modułu współdzielonego (`scrapers/wiki/parsers/elements/*`), aby uniknąć duplikacji domenowej.
  - Kontekst: dodano `text_cleaning.py` i podłączono parsery elementów oraz parser tabel.

## Kryteria ukończenia planu sekcyjnego
- [x] C6. Dodać meta-test CI wykrywający nowy moduł `scrapers/*/sections/*.py` bez aktualizacji coverage snapshot/contract.
  - Kontekst: `tests/test_section_parser_ci_meta.py` porównuje listę modułów sekcji z jawnie utrzymywaną macierzą coverage testów.
- [ ] Każda domena ma co najmniej 3 parsery sekcji działające przez wspólny adapter i wspólny kontrakt wynikowy.
- [x] Każda krytyczna sekcja z `DOMAIN_CRITICAL_SECTIONS` ma fallback aliasów i test regresyjny.
  - Kontekst: rozszerzono aliasy fallback dla `seasons` i `circuits` oraz dodano test obecności aliasów dla wszystkich domen.
- [x] Każdy parser sekcji ma przypisanie do jednej warstwy (`list`/`sections`/`infobox`/`postprocess`) bez mieszania odpowiedzialności.
  - Kontekst: granice warstw zostały zdefiniowane i spięte testem reguły importów dla `sections/`.
