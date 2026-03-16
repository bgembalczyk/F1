# Plan dojścia do docelowej architektury (taski)

> Ten plik jest źródłem prawdy przy zadaniach typu „zaplanuj kolejne taski”.
> Status aktualizujemy checkboxami: `[ ]` / `[x]`.

## Etap 1 — Fundament seed scraperów (Warstwa 0)
- [x] Zdefiniować listę stron startowych (kierowcy, konstruktorzy, GP, tory, sezony).
  - Potwierdzenie: istnieją dedykowane list scrape'ry dla kluczowych seedów (`drivers`, `constructors`, `grands_prix`, `circuits`, `seasons`).
  - Moduły referencyjne: `scrapers/drivers/list_scraper.py`, `scrapers/constructors/*_list*.py`, `scrapers/grands_prix/list_scraper.py`, `scrapers/circuits/list_scraper.py`, `scrapers/seasons/list_scraper.py`.
- [ ] Dodać konfigurację mapującą: `seed_name -> wikipedia_url -> output_category`.
- [ ] Ustalić minimalny wspólny schemat rekordu seed (`name`, `link`, `source_url`, `scraped_at`).
- [ ] Wdrożyć eksport JSON dla każdej kategorii do `data/raw/<category>/`.
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
- [ ] Adapter sekcji: wprowadzić warstwę `SectionSourceAdapter` dla pobierania „kolejnych punktów startowych” bezpośrednio z `data/checkpoints/*.json` (z fallbackiem do `data/raw/*`).
- [ ] Orchestrator 0/1: dodać jawny `StepOrchestrator` (hardcoded flow) wykonujący kroki `L0 -> L1 -> L0/L1` z deklaratywnym `checkpoint_input` i rejestrem kroków.
- [ ] Migracja output layout: przejść z obecnego `data/wiki/...` na layout docelowy (`data/raw`, `data/normalized`, `data/checkpoints`) z mapą kompatybilności ścieżek i etapem migracyjnym.

## Następne 3 konkretne taski (short-term)
- [ ] Task A: Utworzyć konfigurację seed URL-i i kategorii wyjściowych.
  - Skąd bierzemy kolejne punkty startowe: wejście inicjalne z `data/wiki/drivers/f1_drivers.json` oraz `data/wiki/constructors/f1_former_constructors.json` jako bootstrap do pierwszego checkpointu (`data/checkpoints/step_0_layer0.json`).
- [ ] Task B: Ujednolicić format rekordu seed + writer JSON.
  - Skąd bierzemy kolejne punkty startowe: po standaryzacji zapis do `data/raw/<category>/...`; `checkpoint_input` następnego kroku wskazuje konkretny plik `data/raw/drivers/drivers_seed_v1.json`.
- [ ] Task C: Dodać pierwszy pionowy slice end-to-end dla `drivers` z checkpointem wejścia do kolejnego kroku.
  - Skąd bierzemy kolejne punkty startowe: `data/checkpoints/step_1_layer1_drivers.json` (URL-e kierowców po L0) -> wejście do kolejnego kroku L1.
