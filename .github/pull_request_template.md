## Opis zmiany

<!-- Krótko: co i dlaczego zostało zmienione -->

## Checklist (quality gate)

- [ ] **Brak nowych `Any`**: potwierdzone przez gate `Strict typing regression gate (mypy)` (`scripts/ci/mypy_regression_gate.py`).
- [ ] **Granice modułów**: potwierdzone przez `Architecture tests` + `import-linter`.
- [ ] **Duplikacja**: potwierdzona przez `jscpd` + `pylint duplicate-code` (`Static quality gates`).
- [ ] **Architecture impact**: sekcja poniżej jest uzupełniona i przechodzi walidator PR template (`scripts/ci/validate_pr_template.py`).

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
