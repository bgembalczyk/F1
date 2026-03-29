## Opis zmiany

<!-- Krótko: co i dlaczego zostało zmienione -->

## SRP impact

<!-- Jak zmiana wpływa na pojedynczą odpowiedzialność modułów/klas? -->

## DRY impact

<!-- Czy usunięto duplikację, ograniczono powielanie logiki lub pozostawiono bez zmian? -->

## Contracts changed

<!-- Jakie kontrakty/interfejsy/API zmieniły się w tym PR? Jeśli brak: wpisz "Brak". -->

## Backward compatibility

<!-- Czy zmiana jest kompatybilna wstecz? Opisz ryzyka i plan migracji, jeśli potrzebny. -->

## DoD

<!-- Definition of Done dla tego PR (co musi być spełnione przed merge). -->

## Checklista techniczna (obowiązkowa)

- [ ] Testy kontraktowe
- [ ] Brak nowych Any
- [ ] Brak nowych magic strings
- [ ] Zaktualizowany ADR/docs

## Checklist (quality gate)

- [ ] **SRP**: każdy nowy/zmieniony komponent ma jedną, spójną odpowiedzialność.
- [ ] **DIP**: moduły wysokiego poziomu zależą od abstrakcji, nie od implementacji.
- [ ] **Brak nowej duplikacji**: sprawdzone lokalnie (`pylint` duplicate-code / CI static gates).
- [ ] **Zgodność z bazowymi abstrakcjami**: klasy rozszerzają istniejące kontrakty/interfejsy i nie łamią ich API.

## Refactor included

<!-- Wymagane dla każdego PR funkcjonalnego: minimum 1 mikro-refactor redukujący duplikację lub wzmacniający kontrakt OOP. -->

- [ ] Mikro-refactor wykonany (redukcja duplikacji **lub** poprawa kontraktu OOP).
- Typ: <!-- np. DRY / OOP contract -->
- Zakres (pliki/moduły): <!-- krótko -->
- Wpływ na duplikację (linie lub bloki): **usunięto:** <!-- n --> / **dodano:** <!-- n -->
- Notatka o kompatybilności kontraktu: <!-- np. brak zmian API / opis zmian -->

## Code review evidence (wymagane)

<!--
Wymóg code review: przed akceptacją wszystkie checklisty muszą być odhaczone,
a reviewer musi otrzymać dowód w postaci outputu testów/checków.
Wklej poniżej komendy + wynik (np. pytest, mypy, ruff, lint-imports).
-->

```text
# komenda
# output
```
