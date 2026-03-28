# ADR-0001: Kontrakt konfiguracji scraperów

- **Status:** Accepted
- **Data:** 2026-03-28
- **Autor:** zespół F1 parser
- **Decydenci:** maintainers parserów wiki
- **Dotyczy:** konfiguracja scraperów tabelowych

## Kontekst
W kodzie historycznie występowały różne sposoby deklarowania konfiguracji scraperów (`ScraperConfig(...)`, aliasy importów, mieszane style). Utrudniało to review i automatyczną walidację.

## Decyzja
Przyjmujemy jeden kontrakt konfiguracji:
- `CONFIG` budujemy przez `build_scraper_config(...)` z canonical importu `scrapers.base.table.config`.
- Schemat tabeli deklarujemy przez DSL (`column(...)` + `TableSchemaDSL(...)`) albo helper zwracający schema DSL.
- Nie używamy klasowego `CONFIG = ScraperConfig(...)`.
- Nie używamy deprecated aliasu `build_scraper_config` z `scrapers.base.table.builders`.

## Konsekwencje
- Plusy:
  - Spójna deklaracja konfiguracji między domenami.
  - Prostsze reguły CI i review.
- Minusy / trade-offy:
  - Konieczność migracji starszych modułów.
- Ryzyka:
  - Czasowy koszt refaktoryzacji starszego kodu.

## Weryfikacja
- Statyczne reguły CI blokujące niezgodne wzorce konfiguracji.
- Review każdej nowej konfiguracji pod kątem zgodności z DSL.
