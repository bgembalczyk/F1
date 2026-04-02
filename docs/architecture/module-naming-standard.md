# Standard nazewnictwa modułów architektonicznych

Krótki standard dla nazw, które często były mieszane semantycznie (`helpers`, `executor`, `service`, itp.).

## Słownik ról

- **Service**
  - Orkiestruje regułę biznesową lub przypadek użycia.
  - Nie powinien być „workiem” na utilsy techniczne.
  - Nazwa: `<Domena><Akcja>Service` (np. `LayerZeroMergeService`).

- **Factory**
  - Tworzy obiekty konfiguracyjne/instancje i ukrywa szczegóły konstrukcji.
  - Nie wykonuje docelowego use-case end-to-end.
  - Nazwa: `<CoTworzy>Factory` lub `<Kontekst><CoTworzy>Factory`.

- **Runner**
  - Uruchamia pełny przebieg procesu/pipeline/jobu.
  - Zarządza kolejnością kroków i lifecycle.
  - Nazwa: `<Kontekst>Runner`.

- **Adapter**
  - Tłumaczy kontrakt A -> B (API, format, źródło danych, model).
  - Bez logiki biznesowej domeny.
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
3. Jeżeli klasa/moduł uruchamia cały flow, preferuj `Runner` zamiast ogólnego `Executor` w nowym kodzie.

## Checklista review (naming gate)

- [ ] Każdy nowy moduł ma nazwę odzwierciedlającą jedną z ról: `Service`, `Factory`, `Runner`, `Adapter`, `EntryPoint` albo nazwę celu technicznego.
- [ ] Nie dodano nowego pliku o nazwie `helpers.py` bez ADR/uzasadnienia.
- [ ] Jeśli zmieniono mylącą nazwę, zachowano alias legacy + deprecację.
- [ ] Nowe nazwy pól/argumentów/metod nie dublują informacji już zakodowanej w typie (`*_service`, `*_builder`, `*_function` tylko gdy dodają semantykę).
