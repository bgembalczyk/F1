# Reguła review: granica `base` vs domena dla kolumn tabel

## Zasada

Nowe zachowanie **domenowe** nie trafia do `scrapers/base/table/columns/types/` bez jawnego uzasadnienia architektonicznego w PR.

## Definicje

- **Neutralne (`base`)**: typy ogólne (np. `TextColumn`, `UrlColumn`, `RegexColumn`) i mechanizmy kompozycji (`MultiColumn`, `FuncColumn`, fabryki kolumn).
- **Domenowe**: reguły zależne od semantyki F1/encji domenowych (np. kierowca, konstruktor, silnik, opony, punkty, sezony, rundy, pozycja, entrant).

## Wymóg dla review

Jeżeli zmiana dodaje logikę domenową:

1. implementacja musi trafić do `scrapers/<domain>/columns/`,
2. w opisie PR musi znaleźć się krótkie uzasadnienie wyboru domeny,
3. wyjątek (umieszczenie w `base`) wymaga sekcji **"Uzasadnienie dla base"** i wskazania, które domeny korzystają z tej samej reguły bez modyfikacji.

## Dodatkowy gate anty-`helpers.py`

Przy review zmian technicznych obowiązuje dodatkowy warunek:

1. nowe funkcje **nie mogą** domyślnie trafiać do kolejnego `helpers.py`,
2. trzeba wskazać moduł celowy (np. `path_resolver`, `record_merge_ops`, `source_routing`),
3. dopuszczalny jest tymczasowy re-export ze starego modułu `helpers.py`, ale z planem usunięcia aliasu w kolejnych PR-ach.
