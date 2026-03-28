# ADR-0003: Strategia Dependency Injection

- **Status:** Accepted
- **Data:** 2026-03-28
- **Autor:** zespół F1 parser
- **Decydenci:** maintainers warstw orchestration
- **Dotyczy:** warstwy `layers/*` i moduły orkiestracji scraperów

## Kontekst
Rosnąca liczba zależności (parsery, walidatory, transformery, serwisy pomocnicze) utrudnia testowanie i wymianę komponentów przy ciasnym wiązaniu implementacji.

## Decyzja
Przyjmujemy strategię DI opartą o jawne wstrzykiwanie zależności:
- Komponenty domenowe przyjmują zależności przez konstruktor/fabrykę, zamiast tworzyć je wewnątrz metod biznesowych.
- Warstwa orchestration odpowiada za składanie obiektów i wiring.
- Interfejsy kontraktowe (protocol/abstrakcje) są preferowane względem bezpośrednich importów konkretnych implementacji.
- W testach jednostkowych używamy stubów/mocków wstrzykiwanych przez DI.

## Konsekwencje
- Plusy:
  - Lepsza testowalność i modularność.
  - Łatwiejsza wymiana implementacji.
- Minusy / trade-offy:
  - Więcej kodu inicjalizacyjnego (composition root).
- Ryzyka:
  - Niespójne stosowanie DI bez jasnych wytycznych review.

## Weryfikacja
- Review sprawdza brak nowych ukrytych inicjalizacji twardych zależności.
- Testy jednostkowe potwierdzają możliwość podmiany zależności.
