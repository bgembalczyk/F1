# ADR-0008: Governance for compat/shim/alias modules

- **Status:** Accepted
- **Data:** 2026-04-11
- **Autor:** zespół F1 architecture
- **Decydenci:** maintainers
- **Dotyczy:** moduły Pythona zawierające `compat`, `shim`, `alias` w nazwie

## Kontekst
Warstwy przejściowe (`compat`/`shim`/`alias`) zwiększają koszt utrzymania i rozmywają kontrakt architektoniczny. Po zakończeniu migracji utrzymujemy tylko niezbędne adaptery infrastrukturalne.

## Decyzja
- Blokujemy dodawanie nowych modułów `compat`/`shim`/`alias` w kodzie aplikacyjnym.
- Jedynymi zatwierdzonymi wyjątkami infrastrukturalnymi są:
  - `infrastructure/http/type_alias.py`
  - `infrastructure/http/errors/shim/*`
- Reguła jest egzekwowana testem architektonicznym.

## Konsekwencje
- Plusy: spójne API, mniej debtu migracyjnego.
- Minusy: migracje muszą być wykonywane atomowo zamiast etapowych wrapperów.
