# Indeks dokumentacji (canonical)

To jest **jedyny centralny indeks** dokumentacji projektu.
Aby ograniczać duplikację między dokumentami, w innych plikach utrzymujemy tylko krótkie konteksty i linki tutaj.

## Szybki start diagnozy

- [Debug cookbook (Layer 0/1): objaw → gdzie sprawdzić → co poprawić](DEBUG_COOKBOOK.md)

## Architektura warstw

- [Architektura warstw scraperów](scrapers-layer-architecture.md)
- [Granice modułów parserów i layout domen](MODULE_BOUNDARIES.md)
- [Przewodnik rozszerzania scraperów](architecture/scraper-extension-guide.md)

## Kluczowe protokoły / interfejsy

- [ADR index](adr/README.md)
  - [ADR-0001: Kontrakt konfiguracji](adr/0001-configuration-contract.md)
  - [ADR-0002: Kontrakt parserów sekcji](adr/0002-section-parser-contract.md)
  - [ADR-0003: Strategia DI](adr/0003-di-strategy.md)
  - [ADR-0004: Konwencje nazewnictwa hooków](adr/0004-hook-naming-conventions.md)

## Zasady OOP / DRY dla contributorów

- [CHANGES_CHECKLIST (review + merge gate)](CHANGES_CHECKLIST.md)
- [MODULE_BOUNDARIES (reguły zależności i antyduplikacja)](MODULE_BOUNDARIES.md)
- [TYPING_GUARDRAILS](TYPING_GUARDRAILS.md)


## README modułów (quick orientation)

- [layers/zero README](../layers/zero/README.md)
- [layers/one README](../layers/one/README.md)
- [scrapers/base README](../scrapers/base/README.md)
- [infrastructure/http_client README](../infrastructure/http_client/README.md)

## UML i dokumentacja pomocnicza

- [Index dokumentacji UML](INDEX_DOKUMENTACJI_UML.md)
- [UML diagrams README (EN)](UML_DIAGRAMS_README.md)
- [UML diagrams README (PL)](UML_DIAGRAMS_README_PL.md)
- [Debug cookbook (objaw → gdzie szukać)](DEBUG_COOKBOOK.md)

## Roadmapa / przyszły kierunek

- [FUTURE_VISION_DATASET_PIPELINE](FUTURE_VISION_DATASET_PIPELINE.md)
- [ROADMAP_TASKS_DATASET_ML](ROADMAP_TASKS_DATASET_ML.md)

## Checklista: dodawanie nowej domeny / komponentu

- [ ] Potwierdź granice warstw i kierunki importów (`MODULE_BOUNDARIES.md`).
- [ ] Zweryfikuj czy da się użyć/rozszerzyć `scrapers/base/*` zamiast duplikacji.
- [ ] Zadbaj o kontrakty (typy/interfejsy) i zgodność z ADR.
- [ ] Dodaj lub uzupełnij dokumentację domenową (`scrapers/<domain>/README.md`).
- [ ] Dodaj/uzupełnij testy i checks wymagane przez CI.
- [ ] Dla zmiany architektonicznej dodaj nowy ADR albo aktualizację ADR.
