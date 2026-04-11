# ADR-0007: Canonical API parserów sekcji

- **Status:** Accepted
- **Data:** 2026-04-11
- **Autor:** zespół F1 parser
- **Decydenci:** maintainers parserów domenowych
- **Dotyczy:** `scrapers/parsers/section/*`, `scrapers/parsers/roles.py`

## Kontekst
W kodzie istniały równoległe definicje kontraktu parserów sekcji (`protocol.py`, `section_parser_protocol.py` i lokalne protokoły). Powodowało to rozjazdy sygnatur i niejednoznaczność API.

## Decyzja
- Kanoniczny kontrakt parsera pozostaje oparty o `scrapers/domain_roles.py::Parser[InputT, OutputT]`.
- Dla parserów sekcji używamy jednej specjalizacji: `scrapers.parsers.roles.SectionParser = Parser[BeautifulSoup, SectionParseResult]`.
- Jedyna poprawna sygnatura parsera sekcji to:
  - `parse(fragment: BeautifulSoup) -> SectionParseResult`.
- Moduły `scrapers/parsers/section/protocol.py` i `scrapers/parsers/section/section_parser_protocol.py` nie są traktowane jako aktywna ścieżka wsparcia; obowiązuje import z kanonicznego kontraktu.
- Nazewnictwo fabryk/rejestrów nie używa `parse`; API `parse` jest zarezerwowane dla parserów.

## Konsekwencje
- Plusy:
  - Jedno źródło prawdy dla API parserów sekcji.
  - Lepsza czytelność adnotacji i prostsze typowanie.
- Minusy / trade-offy:
  - Potrzeba migracji starych importów do `scrapers.parsers.roles.SectionParser`.
- Ryzyka:
  - Niewidoczne miejsca z niestandardową sygnaturą mogą wymagać późniejszego cleanupu.

## Weryfikacja
- Lint/typecheck i testy parserów sekcji.
- Review importów, aby nowe implementacje korzystały z `scrapers.parsers.roles.SectionParser`.
