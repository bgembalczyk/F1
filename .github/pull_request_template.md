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
- [ ] Spójność terminologii domenowej (zgodnie z `docs/DOMAIN_GLOSSARY.md`)

## Checklist (quality gate)

- [ ] **Brak nowych `Any`**: potwierdzone przez gate `Strict typing regression gate (mypy)` (`scripts/ci/mypy_regression_gate.py`).
- [ ] **Granice modułów**: potwierdzone przez `Architecture tests` + `import-linter`.
- [ ] **Duplikacja**: potwierdzona przez `jscpd` + `pylint duplicate-code` (`Static quality gates`).
- [ ] **Architecture impact**: sekcja poniżej jest uzupełniona i przechodzi walidator PR template (`scripts/ci/validate_pr_template.py`).
- [ ] **Terminologia domenowa**: brak niedozwolonych wariantów nazw (`python scripts/check_domain_terminology.py`).

## Architecture impact

<!-- Pole wymagane. Dla PR bez zmian w `scrapers/base/` wpisz jawnie: "nie dotyczy". -->

- Zmiany w `scrapers/base/`: 
- Dotknięte domeny: 
- Kompatybilność wsteczna: 
- Migracja wymagana: 

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
