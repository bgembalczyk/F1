# Standard nazewnictwa modułów architektonicznych

Krótki standard dla nazw, które często były mieszane semantycznie (`helpers`, `executor`, `service`, itp.).

## Słownik ról

- **Service**
  - Orkiestruje regułę biznesową lub przypadek użycia.
  - Nie powinien być „workiem” na utilsy techniczne.
  - Powinien być idempotentny względem wejścia (brak ukrytych efektów ubocznych poza jawnie opisaną integracją I/O).
  - Nazwa: `<Domena><Akcja>Service` (np. `LayerZeroMergeService`).

- **Factory**
  - Tworzy obiekty konfiguracyjne/instancje i ukrywa szczegóły konstrukcji.
  - Nie wykonuje docelowego use-case end-to-end.
  - Dopuszczalna logika walidacji wejścia, ale bez „uruchamiania procesu”.
  - Nazwa: `<CoTworzy>Factory` lub `<Kontekst><CoTworzy>Factory`.

- **Runner**
  - Uruchamia pełny przebieg procesu/pipeline/jobu.
  - Zarządza kolejnością kroków i lifecycle.
  - Może wołać wiele `Service`, ale nie powinien implementować ich logiki domenowej inline.
  - Nazwa: `<Kontekst>Runner`.

- **Adapter**
  - Tłumaczy kontrakt A -> B (API, format, źródło danych, model).
  - Bez logiki biznesowej domeny.
  - Ma być wymienialny (łatwy do podmiany w testach i integracjach).
  - Nazwa: `<ŹródłoLubCel>Adapter`.

- **EntryPoint**
  - Punkt wejścia (CLI, domain bootstrap, external trigger).
  - Powinien delegować, a nie implementować ciężką logikę.
  - Nazwa: `<Kontekst>EntryPoint`.

## Reguły praktyczne

0. **Reguła składni nazwy (max 3 człony)**.
   - Stosuj schemat: `czasownik + obiekt + (opcjonalny kontekst)`.
   - Przykłady: `build_runner_map`, `merge_layer_zero`, `export_results_csv`.
   - Nie doklejaj członów, które dublują już informację z typu pola/klasy.
1. **Unikaj nowych `helpers.py`**.
   - Preferuj nazwy celu, np. `runner_registry.py`, `run_profile_paths.py`, `seed_record_projection.py`.
2. Dla istniejących mylących nazw stosuj migrację bez breaking change:
   - nowy moduł o nazwie semantycznej,
   - stary moduł jako alias/re-export + `DeprecationWarning`.
   - re-export usuwaj etapami (najpierw migracja importów wewnętrznych, potem usunięcie aliasu w kolejnym PR).
3. W obszarach technicznych preferuj moduły celowe zamiast jednego worka:
   - `path_resolver.py` (rozwiązywanie ścieżek),
   - `record_merge_ops.py` (operacje merge rekordów),
   - `source_routing.py` (wybór i routing źródeł danych).
4. Jeżeli klasa/moduł uruchamia cały flow, preferuj `Runner` zamiast ogólnego `Executor` w nowym kodzie.

## Szybkie drzewko decyzyjne (Service vs Factory vs Runner vs Adapter)

1. **Czy kod uruchamia cały pipeline/job?**  
   -> użyj `Runner`.
2. **Czy kod tworzy/konfiguruje obiekt(y) i zwraca je bez uruchamiania flow?**  
   -> użyj `Factory`.
3. **Czy kod mapuje format/kontrakt A na B?**  
   -> użyj `Adapter`.
4. **Czy kod realizuje regułę biznesową/use-case?**  
   -> użyj `Service`.
5. **Jeśli pasuje więcej niż jedna rola**: rozdziel moduł na mniejsze komponenty; nazwa modułu ma wskazywać dominującą odpowiedzialność.

## Checklista review (naming gate)

- [ ] Każdy nowy moduł ma nazwę odzwierciedlającą jedną z ról: `Service`, `Factory`, `Runner`, `Adapter`, `EntryPoint` albo nazwę celu technicznego.
- [ ] Nie dodano nowego pliku o nazwie `helpers.py` bez ADR/uzasadnienia.
- [ ] Dla nowych funkcji technicznych wybrano moduł celowy zamiast dokładania kolejnych symboli do istniejącego `helpers.py`.
- [ ] Jeśli zmieniono mylącą nazwę, zachowano alias legacy + deprecację.
- [ ] Nowe nazwy pól/argumentów/metod nie dublują informacji już zakodowanej w typie (`*_service`, `*_builder`, `*_function` tylko gdy dodają semantykę).
