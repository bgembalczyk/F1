# Architecture Decision Records (ADR)

Ten katalog przechowuje **trwałe decyzje architektoniczne** projektu.

## Zasady

1. Każda nowa decyzja architektoniczna dostaje kolejny numer ADR (`NNNN`).
2. Każda większa zmiana architektoniczna w PR musi mieć referencję do co najmniej jednego ADR (np. `ADR-0002`).
3. Jeżeli zmiana modyfikuje wcześniej zatwierdzoną zasadę, PR musi zawierać aktualizację istniejącego ADR lub nowy ADR, który go zastępuje.
4. Brak referencji ADR dla zmian architektonicznych traktujemy jako blokadę na review.

## Lista decyzji

- [ADR-0001](0001-configuration-contract.md): Kontrakt konfiguracji scraperów.
- [ADR-0002](0002-section-parser-contract.md): Kontrakt parserów sekcji.
- [ADR-0003](0003-di-strategy.md): Strategia Dependency Injection.
- [ADR-0004](0004-hook-naming-conventions.md): Zasady nazewnictwa hooków.

## Jak dodać nowy ADR

1. Skopiuj [szablon](0000-template.md).
2. Nadaj kolejny numer i konkretny tytuł.
3. Ustaw status (`Proposed` -> `Accepted` po zatwierdzeniu).
4. Podlinkuj ADR w dokumentacji i opisie PR.
