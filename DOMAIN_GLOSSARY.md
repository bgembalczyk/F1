# DOMAIN GLOSSARY

Ten dokument definiuje **canonical terminy domenowe** używane w kodzie, nazwach klas, nazwach pól i dokumentacji.

## Canonical terminy

| Pojęcie | Canonical forma | Niedozwolone synonimy / aliasy |
|---|---|---|
| Grand Prix | `grand_prix` | `grandprix`, `grand-prix` |
| Wielka liczba mnoga Grand Prix | `grands_prix` | `grandprixes`, `grand_prixes` |
| Konstruktor F1 | `constructor` | `team` *(w nazwach pól/klas domenowych)* |
| Sezon F1 | `season` | `championship_year` |

## Zasady nazewnicze (pola i klasy)

1. Dla pojęć z tabeli powyżej używamy wyłącznie form canonical.
2. W Pythonie:
   - pola/zmienne: `snake_case` (np. `grand_prix_name`),
   - klasy: `PascalCase` bazujące na canonical termach (np. `GrandPrixParser`, nie `GrandprixParser`).
3. Jeżeli domenowo potrzebny jest termin biznesowy różny od canonical, należy:
   - opisać to w PR,
   - dodać wyjątek do skryptu CI `scripts/ci/check_terminology_consistency.py`.

## Egzekucja w CI

Spójność terminologiczna jest sprawdzana przez:

- `scripts/ci/check_terminology_consistency.py`

Skrypt analizuje zmienione pliki i wykrywa użycie zabronionych synonimów.
