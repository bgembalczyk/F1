# Plan dojścia do docelowej architektury (taski)

> Ten plik jest źródłem prawdy przy zadaniach typu „zaplanuj kolejne taski”.
> Status aktualizujemy checkboxami: `[ ]` / `[x]`.

## Etap 1 — Fundament seed scraperów (Warstwa 0)
- [ ] Zdefiniować listę stron startowych (kierowcy, konstruktorzy, GP, tory, sezony).
- [ ] Dodać konfigurację mapującą: `seed_name -> wikipedia_url -> output_category`.
- [ ] Ustalić minimalny wspólny schemat rekordu seed (`name`, `link`, `source_url`, `scraped_at`).
- [ ] Wdrożyć eksport JSON dla każdej kategorii do `data/raw/<category>/`.
- [ ] Dodać logowanie jakości: liczba rekordów, puste pola, duplikaty.

## Etap 2 — Parsery encji szczegółowych (Warstwa 1)
- [ ] Dodać parser infoboxów dla stron encji (driver/constructor/circuit/grand_prix/season).
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
- [ ] Dodać retry/backoff dla fetchowania stron.

## Etap 5 — Przygotowanie pod ML (później)
- [ ] Zdefiniować cechy i słowniki tokenizacji.
- [ ] Dodać etap kodowania cech do `data/ml_ready/`.
- [ ] Zbudować wersjonowane zestawy treningowe.

## Następne 3 konkretne taski (short-term)
- [ ] Task A: Utworzyć konfigurację seed URL-i i kategorii wyjściowych.
- [ ] Task B: Ujednolicić format rekordu seed + writer JSON.
- [ ] Task C: Dodać pierwszy pionowy slice end-to-end dla `drivers` z checkpointem wejścia do kolejnego kroku.


## Etap 0.5 — Ujednolicenie struktury domen parserów (NOWE)
- [x] Dodać spójny podział katalogów domenowych: `list/`, `sections/`, `infobox/`, `postprocess/`.
- [x] Wydzielić logikę sekcyjną z parserów single/list do `sections/` (driver results, grand prix by year, season adapters: calendar/results/standings).
- [x] Wprowadzić wspólny interfejs parsera sekcyjnego (`SectionParseResult`, `SectionParser`).
- [x] Dodać mapę `DOMAIN_CRITICAL_SECTIONS` (`section_id`, `alternative_section_ids`) i użyć jej jako fallbacku w parserach GP.
- [ ] Migrować kolejne parsery domenowe (constructors/circuits) na nowy interfejs sekcyjny.
