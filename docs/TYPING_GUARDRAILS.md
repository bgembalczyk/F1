# Typing guardrails (phase 1)

## Scope
- `scrapers/base/`
- `scrapers/*/sections/`

W tej iteracji uruchamiamy „strict typing” na najbardziej krytycznych modułach
pipeline (kontrakty + konfiguracja + interfejs sekcji).

## Niedozwolone skróty
1. **`Any` poza granicami I/O**
   - dozwolone tylko na styku z niekontrolowanym wejściem/wyjściem (np. surowe JSON/HTTP, serializacja).
   - wewnątrz pipeline i interfejsów domenowych używamy `object`, aliasów domenowych lub `Protocol`.
2. **Brak adnotacji typów zwrotnych w publicznych metodach**
   - publiczna metoda/funkcja (`def name(...)`) musi mieć jawny return type.
3. **Niejawne opcjonalności**
   - `None` musi być jawnie zapisane (`X | None`), bez implicit optional.
4. **Niekompletne adnotacje definicji**
   - wszystkie parametry i return type muszą być typowane.

## Bramka regresji
- `mypy.ini` uruchamia zestaw strict reguł dla krytycznych modułów:
  - `scrapers/base/pipeline_runner.py`
  - `scrapers/base/options.py`
  - `scrapers/base/table/pipeline.py`
  - `scrapers/base/sections/interface.py`
- CI blokuje PR przy regresji (`mypy --config-file mypy.ini`).
