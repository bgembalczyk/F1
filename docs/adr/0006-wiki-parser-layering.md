# ADR-0006: Warstwowanie parserów Wiki (Element → Structure → Domain Mapper)

- **Status:** Accepted
- **Data:** 2026-04-11
- **Autor:** zespół F1 parser
- **Decydenci:** maintainers parserów wiki i domenowych
- **Dotyczy:** `scrapers/parsers/wiki/*`, `scrapers/parsers/section/*`, `scrapers/parsers/table/wiki/*`, usługi domenowe wykorzystujące parsery wiki

## Kontekst
Parsery HTML Wikipedii były rozwijane iteracyjnie. W praktyce pojawiały się miejsca, gdzie logika domenowa dotykała bezpośrednio implementacji parserów wiki (np. bezpośrednia zależność od klas konkretnych parserów tabel). Utrudnia to wymianę parserów i testowanie granic odpowiedzialności.

## Decyzja
Wprowadzamy i utrwalamy 3-warstwową hierarchię:

1. **Element Parser**
   - odpowiedzialność: parsowanie pojedynczego `Tag` (np. nagłówek, paragraf, lista, tabela, infobox, navbox, refs),
   - rodzina: `scrapers/parsers/wiki/`.

2. **Structure Parser**
   - odpowiedzialność: kompozycja sekcji/podsekcji i nawigacja po nagłówkach,
   - rodzina: `scrapers/parsers/section/`.

3. **Domain Mapper**
   - odpowiedzialność: mapowanie danych parserów wiki (w szczególności tabel) na rekordy domenowe,
   - rodzina: `scrapers/parsers/table/wiki/`.

Podejście jest **section-first**: parser sekcji to główny punkt wejścia,
a parsery elementarne są narzędziami dobieranymi przez parser sekcji
(np. przez `SectionParserToolbox`).

Dodatkowo stabilizujemy granice przez interfejsy/kontrakty:
- `WikiElementParser` (`scrapers/parsers/wiki/contracts.py`),
- `StructureParser` (`scrapers/parsers/section/contracts.py`),
- `WikiTableDomainMapper` i `ArticleTablesParserProtocol` (`scrapers/parsers/table/wiki/contracts.py`).


### Tabela kontraktów parserów (canonical)

| Kontrakt | Wejście HTML | Wyjście strukturalne | Odpowiedzialność parsera |
| --- | --- | --- | --- |
| `Parser[InputT, OutputT]` (`scrapers/domain_roles.py`) | `InputT` (np. `BeautifulSoup`, `Tag`) | `OutputT` | Kanoniczny interfejs `parse(...)` dla transformacji HTML/tekst → struktura. |
| `WikiSectionParser` | `BeautifulSoup` sekcji/artykułu | `list[dict[str, Any]]` (`WikiRecords`) | Agregacja sekcji artykułu do rekordów o stałym kształcie. |
| `WikiTableParser` | `BeautifulSoup` z tabelami | `list[dict[str, Any]]` (`WikiRecords`) | Ekstrakcja i normalizacja danych tabelarycznych Wiki. |
| `WikiListParser` | `Tag` (`<ul>`/`<ol>`) | `list[dict[str, Any]]` (`WikiRecords`) | Parsowanie list do rekordów strukturalnych. |
| `WikiTagParser[OutputT]` | pojedynczy `Tag` | `OutputT` | Parsowanie pojedynczego elementu HTML do wyspecjalizowanego DTO/struktury. |

## Granice zależności
- Domena (np. kierowcy/sezony/konstruktorzy) **może zależeć wyłącznie od kontraktów** parserów wiki.
- Implementacje parserów wiki **nie zależą od domeny**.
- Integracja odbywa się przez wstrzykiwanie implementacji kontraktów (DI), nie przez hard-coded importy klas konkretnych.

## Konsekwencje
- Plusy:
  - spójna separacja odpowiedzialności,
  - prostsze testy kontraktowe,
  - mniejsze ryzyko sprzężenia zwrotnego między domeną a parserami.
- Minusy / trade-offy:
  - więcej artefaktów interfejsów i typów pośrednich,
  - konieczność pilnowania granic importów przy review.

## Weryfikacja
- Testy kontraktowe parserów rodzin scraperów.
- Review importów: domena importuje protokoły, nie konkretne implementacje parserów wiki.
- Referencja architektoniczna dla zmian parserów: **ADR-0006**.
