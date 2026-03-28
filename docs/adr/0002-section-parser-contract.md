# ADR-0002: Kontrakt parserów sekcji

- **Status:** Accepted
- **Data:** 2026-03-28
- **Autor:** zespół F1 parser
- **Decydenci:** maintainers parserów domenowych
- **Dotyczy:** `scrapers/*/sections/*`

## Kontekst
Parsery sekcji są krytyczne dla jakości danych i były rozwijane ewolucyjnie. Potrzebny jest jednoznaczny kontrakt wejścia/wyjścia i zestaw bramek jakości.

## Decyzja
Utrzymujemy kontrakt parserów sekcji oparty o:
- Ustandaryzowany wynik parsowania (`SectionParseResult` + metadata parsera).
- Obowiązkowe testy snapshot (`minimal + edge`) i testy aliasów sekcji.
- Obowiązkowe testy kontraktowe parsera sekcji.
- Aktualizację dokumentacji domeny przy zmianie parsera sekcji.

## Konsekwencje
- Plusy:
  - Mniej regresji przy zmianach struktury HTML.
  - Spójny interfejs parserów między domenami.
- Minusy / trade-offy:
  - Więcej pracy testowej przy każdej zmianie parsera.
- Ryzyka:
  - Możliwe opóźnienia merge'y przy rozbudowie macierzy snapshotów.

## Weryfikacja
- Merge-gate CI dla `scrapers/*/sections/*.py`.
- Review obejmujące testy kontraktu, snapshot i aliasy.
