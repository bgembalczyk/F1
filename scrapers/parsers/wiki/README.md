# Wiki parsers – architektura warstw

Ten katalog utrzymuje parsery odpowiedzialne za ekstrakcję treści z HTML-a Wikipedii.

## Ustalona hierarchia

Parsery są podzielone na cztery warstwy odpowiadające elementom HTML Wikipedii:

1. **HTML Element Parser** (`scrapers/parsers/html_elements/`)
   - odpowiedzialność: parsuje pojedynczy `bs4.Tag` do prostego słownika,
   - klasa bazowa: `BaseHtmlElementParser[T]` (dla `Tag`) lub `BaseHtmlSectionParser[T]` (dla `BeautifulSoup`),
   - brak logiki domenowej ani zależności od wiki-specyficznych klas.

2. **Wiki Element Parser Contracts** (`scrapers/parsers/contracts/wiki_elements.py`)
   - odpowiedzialność: centralne ABC dla parserów HTML Wikipedii z jednoznacznymi typami I/O,
   - rodziny:
     - `WikiTableParserABC` (`Tag -> dict[str, Any]`),
     - `WikiListParserABC` (`Tag -> dict[str, Any]`),
     - `WikiSectionParserABC` (`BeautifulSoup/Tag -> dict[str, Any]`),
     - `WikiInfoboxParserABC` (`Tag -> InfoboxParsedData`),
     - `WikiNavboxParserABC` (`Tag -> NavBoxParsedData`),
     - `WikiFigureParserABC` (`Tag -> FigureParsedData`).
   - każdy parser elementu wiki dziedziczy po odpowiedniej rodzinie.

3. **Wiki Element Parser** (`scrapers/parsers/wiki/`)
   - odpowiedzialność: konkretne implementacje parserów elementów HTML Wikipedii,
   - implementacje rodzin: `element_table.py`, `element_list.py`, `element_section.py`,
     `element_infobox.py`, `element_navbox.py`, `element_figure.py`.

4. **Structure Parser** (`scrapers/parsers/section/`)
   - odpowiedzialność: kompozycja sekcji/podsekcji i nawigacja po nagłówkach h2–h5,
   - kontrakt: `WikiSectionParserABC` (dla parserów przyjmujących `BeautifulSoup`/`Tag`, zwracających
     `SectionParseResult`) lub `NestedWikiSectionParser` (dla hierarchicznych parserów sekcji
     przyjmujących `Tag` i zwracających `dict`),
   - parsery sekcji dobierają zestaw parserów elementarnych przez `SectionParserToolbox`.

5. **Table Domain Mapper** (`scrapers/parsers/table/wiki/`)
   - odpowiedzialność: mapowanie już sparsowanych danych tabelarycznych (`dict`) na rekordy domenowe,
   - klasa bazowa: `WikiTableBaseMapper` (przyjmuje `dict`, zwraca `dict`),
   - **WAŻNE:** `WikiTableBaseMapper` i jego podklasy NIE parsują HTML — przetwarzają dane
     wyjściowe parsera HTML tabeli. Są mapperami domenowymi, nie parserami HTML.

Pełna decyzja architektoniczna: `ADR-0006`.

## Diagram klas (uproszczony)

```
Wiki*ParserABC (contracts/wiki_elements.py)
  ├── WikiTableParserABC
  ├── WikiListParserABC
  ├── WikiSectionParserABC
  ├── WikiInfoboxParserABC
  ├── WikiNavboxParserABC
  └── WikiFigureParserABC

Concrete wiki HTML parsers
  ├── WikiTableElementParser / WikiTableHtmlParser
  ├── WikiListElementParser
  ├── WikiSectionElementParser
  ├── WikiInfoboxElementParser / WikiInfoboxParser
  ├── WikiNavboxElementParser / WikiNavboxParser
  └── WikiFigureElementParser / WikiFigureParser

WikiTableBaseMapper   [DOMAIN MAPPER – wejście: dict, nie Tag]
  ├── DriverOrderedTableParser  (scrapers/parsers/table/base_ordered.py)
  │   └── DriversListTableParser
  ├── StandingsTableMapper
  ├── RaceResultsTableMapper
  ├── LapRecordsWikiTableMapper
  ├── CircuitsListTableMapper
  └── ... (inne parsery tabel domenowych)

WikiSectionParserABC [ABC – BeautifulSoup/Tag → SectionParseResult]
  └── ... (konkretne parsery sekcji artykułów)

NestedWikiSectionParser [Tag → dict, hierarchiczne sekcje]
  ├── RedFlaggedRacesSectionParser
  └── PointsScoringSystemsSectionParser  (in scrapers/parsers_points.py)
```

## Section-first orchestration

Dla użytkownika końcowego parser sekcji jest bardziej intuicyjnym entrypointem.
Dlatego parsery w `scrapers/parsers/section/` dobierają zestaw parserów elementarnych
wyłącznie przez jawny `SectionParserToolbox` / factory i delegują parsing HTML do parserów
rodzin wiki.


## Rodzina parserów elementarnych (`scrapers/parsers/wiki/`)

- `header.py` – nagłówek (`<header class="mw-body-header">`).
- `paragraph.py` – paragraf (`<p>`).
- `list.py` – lista (`<ul>` / `<ol>`).
- `../table/wiki/table.py` – tabela wikitable (`<table class="wikitable">`, rodzina `WikiTableParserABC`).
- `infobox.py` – infobox (`<table class="infobox">`).
- `navbox.py` – navbox (`<div class="navbox">`).
- `references_wrap.py` – sekcja przypisów (`<div class="references-wrap">`).
- `figure.py` – rysunek (`<figure>`).

## Granice odpowiedzialności

- Parsery elementarne nie mapują bezpośrednio na rekordy domenowe.
- Parsery sekcji składają strukturę i przekazują dane niżej/wyżej, bez logiki domenowej.
- Mappery domenowe tabel wiki (`WikiTableBaseMapper`) realizują mapowanie kolumn i normalizację
  rekordów — przyjmują `dict` (dane po parsowaniu HTML), nie `Tag`.
- Moduły domenowe korzystają z parserowych kontraktów ABC, nie z odwrotnych zależności
  parser → domena.

## Konwencje nazewnicze

Twarde reguły:

- parser HTML/tekst musi udostępniać publiczne `parse(input) -> output`,
- mapper domenowy używa suffixu `*Mapper` i publicznego `map(...)`,
- etap pipeline używa suffixu `*Stage` lub `*Processor` i publicznego `run(...)`.

### do not use Parser suffix unless parse() is public entrypoint

Suffix `Parser` jest zarezerwowany wyłącznie dla klas, których publicznym entrypointem
jest `parse(...)`. Jeśli klasa mapuje dane domenowe po parsowaniu HTML, stosuj `*Mapper`.
Jeśli klasa jest etapem orkiestracji pipeline, stosuj `*Stage`/`*Processor` z `run(...)`.

| Suffix klasy | Wejście | Wyjście | Klasa bazowa |
|---|---|---|---|
| `*TableParser` (HTML) | `Tag` (`<table>`) | `dict` | `WikiTableHtmlParser` |
| `*TableMapper` (domain) | `dict` | `dict` | `WikiTableBaseMapper` |
| `*ListParser` | `Tag` (`<ul>`/`<ol>`) | `dict` | `ListParser` / `WikiListParser` |
| `*SectionParser` | `BeautifulSoup`/`Tag` | `SectionParseResult` | `WikiSectionParserABC` |
| `*SectionParser` (nested) | `Tag` | `dict` | `NestedWikiSectionParser` |
| `*InfoboxParser` | `Tag` (`<table class="infobox">`) | `dict` | `WikiInfoboxElementParserBase` |


## Strict pipeline parserów elementowych

Dla parserów elementowych obowiązuje sztywny pipeline:

1. `Element parser (HTML -> payload)`
2. `Classifier` (opcjonalny)
3. `Mapper/Factory (payload -> rekord transportowy/domenowy)`

Dla wiki runtime realizują to:

- `element_registry.py` – tylko wybór parsera po typie elementu i kontekście,
- `element_dispatcher.py` – orkiestracja parse -> factory,
- `element_payload_factory.py` – classifier + mapper/factory do `WikiParsedPayload`.

Dzięki temu parsery `element_*` pozostają czysto syntaktyczne (HTML -> payload), bez domenowych business rules.
