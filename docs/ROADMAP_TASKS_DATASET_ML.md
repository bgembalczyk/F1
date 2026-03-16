# Plan dojścia do docelowej architektury (taski)

> Ten plik jest źródłem prawdy przy zadaniach typu „zaplanuj kolejne taski”.
> Status aktualizujemy checkboxami: `[ ]` / `[x]`.

## Etap 1 — Fundament seed scraperów (Warstwa 0)
- [ ] Zdefiniować listę stron startowych (kierowcy, konstruktorzy, GP, tory, sezony).
- [x] Dodać konfigurację mapującą: `seed_name -> wikipedia_url -> output_category`. (Wdrożono mapowanie `output_category + output_layer` przez `scrapers/base/output_layout.py` i `RunConfig`).
- [ ] Ustalić minimalny wspólny schemat rekordu seed (`name`, `link`, `source_url`, `scraped_at`).
- [x] Wdrożyć eksport JSON dla każdej kategorii do `data/raw/<category>/`. (Warstwa seed scraperów zapisuje do `raw` przez `output_layer="raw"`).
- [ ] Dodać logowanie jakości: liczba rekordów, puste pola, duplikaty.

## Etap 2 — Parsery encji szczegółowych (Warstwa 1)
- [ ] Dodać parser infoboxów dla stron encji (driver/constructor/circuit/grand_prix/season).
- [ ] Znormalizować kluczowe pola (daty, kraj, aliasy nazw).
- [ ] Dodać mapowanie i wersjonowanie schematów rekordów.
- [x] Zapisywać wynik w `data/normalized/<category>/`. (Warstwa danych pogłębionych zapisuje do `normalized` oraz opcjonalnie do legacy outputu).

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


## Checklist migracji outputów
- [x] Dodać abstrakcję mapowania `category + layer -> output_dir`.
- [x] Przenieść seed listy do `data/raw/<category>/...`.
- [x] Przenieść dane po normalizacji do `data/normalized/<category>/...`.
- [x] Utrzymać tryb kompatybilny: równoległy zapis do `data/wiki/...` (flaga `legacy_output_enabled`).
- [x] Rozszerzyć metadane zapisu (`source_url`, `scraped_at`, `parser_version`, `schema_version`).
- [ ] Zweryfikować brak konsumentów zależnych od `data/wiki/...` (CLI, notebooki, joby offline).
- [ ] Przełączyć domyślne pipeline na nowe ścieżki bez fallbacków.

### Kryterium „gotowe do wyłączenia legacy outputu”
- [ ] Wszystkie consumer-y czytają wyłącznie `data/raw` i `data/normalized`.
- [ ] Co najmniej 2 pełne przebiegi pipeline bez regresji względem `data/wiki`.
- [ ] Monitoring i raporty jakości nie odwołują się do starej struktury katalogów.
- [ ] Flaga `legacy_output_enabled` może zostać ustawiona domyślnie na `False` bez utraty funkcjonalności.
