# Wiki parsers – architektura warstw

Ten katalog utrzymuje parsery odpowiedzialne za ekstrakcję treści z HTML-a Wikipedii.

## Ustalona hierarchia

Parsery są podzielone na cztery warstwy odpowiadające elementom HTML Wikipedii:

1. **HTML Element Parser** (`scrapers/parsers/html_elements/`)
   - odpowiedzialność: parsuje pojedynczy `bs4.Tag` do prostego słownika,
   - klasa bazowa: `BaseHtmlElementParser[T]` (dla `Tag`) lub `BaseHtmlSectionParser[T]` (dla `BeautifulSoup`),
   - brak logiki domenowej ani zależności od wiki-specyficznych klas.

2. **Wiki Element Parser Families** (`scrapers/parsers/wiki/families.py`)
   - odpowiedzialność: centralne ABC dla parserów HTML Wikipedii z jednoznacznymi typami I/O,
   - rodziny:
     - `WikiTableHtmlParserABC` (`Tag -> dict[str, Any]`),
     - `WikiListHtmlParserABC` (`Tag -> dict[str, Any]`),
     - `WikiSectionHtmlParserABC` (`BeautifulSoup -> dict[str, Any]`),
     - `WikiInfoboxHtmlParserABC` (`Tag -> InfoboxParsedData`),
     - `WikiNavboxHtmlParserABC` (`Tag -> NavBoxParsedData`),
     - `WikiFigureHtmlParserABC` (`Tag -> FigureParsedData`).
   - każdy parser elementu wiki dziedziczy po odpowiedniej rodzinie.

3. **Wiki Element Parser** (`scrapers/parsers/wiki/`)
   - odpowiedzialność: konkretne implementacje parserów elementów HTML Wikipedii,
   - implementacje rodzin: `element_table.py`, `element_list.py`, `element_section.py`,
     `element_infobox.py`, `element_navbox.py`, `element_figure.py`.

4. **Structure Parser** (`scrapers/parsers/section/`)
   - odpowiedzialność: kompozycja sekcji/podsekcji i nawigacja po nagłówkach h2–h5,
   - kontrakt: `SectionParser` (dla parserów przyjmujących `BeautifulSoup`, zwracających
     `SectionParseResult`) lub `NestedWikiSectionParser` (dla hierarchicznych parserów sekcji
     przyjmujących `Tag` i zwracających `dict`),
   - parsery sekcji dobierają zestaw parserów elementarnych przez `SectionParserToolbox`.

5. **Table Domain Mapper** (`scrapers/parsers/table/wiki/`)
   - odpowiedzialność: mapowanie już sparsowanych danych tabelarycznych (`dict`) na rekordy domenowe,
   - klasa bazowa: `WikiTableBaseParser` (przyjmuje `dict`, zwraca `dict`),
   - **WAŻNE:** `WikiTableBaseParser` i jego podklasy NIE parsują HTML — przetwarzają dane
     wyjściowe parsera HTML tabeli. Są mapperami domenowymi, nie parserami HTML.

Pełna decyzja architektoniczna: `ADR-0006`.

## Diagram klas (uproszczony)

```
Wiki*HtmlParserABC (families.py)
  ├── WikiTableHtmlParserABC
  ├── WikiListHtmlParserABC
  ├── WikiSectionHtmlParserABC
  ├── WikiInfoboxHtmlParserABC
  ├── WikiNavboxHtmlParserABC
  └── WikiFigureHtmlParserABC

Concrete wiki HTML parsers
  ├── WikiTableElementParser / WikiTableHtmlParser
  ├── WikiListElementParser
  ├── WikiSectionElementParser
  ├── WikiInfoboxElementParser / WikiInfoboxParser
  ├── WikiNavboxElementParser / WikiNavboxParser
  └── WikiFigureElementParser / WikiFigureParser

WikiTableBaseParser   [DOMAIN MAPPER – wejście: dict, nie Tag]
  ├── DriverOrderedTableParser  (scrapers/parsers/table/base_ordered.py)
  │   └── DriversListTableParser
  ├── MappedWikiTableParser
  │   ├── StandingsTableParser
  │   ├── RaceResultsTableParser
  │   ├── LapRecordsWikiTableParser
  │   └── CircuitsListTableParser
  └── ... (inne parsery tabel domenowych)

SectionParser [Protocol – BeautifulSoup → SectionParseResult]
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
- `../table/wiki/table.py` – tabela wikitable (`<table class="wikitable">`, rodzina `WikiTableHtmlParserABC`).
- `infobox.py` – infobox (`<table class="infobox">`).
- `navbox.py` – navbox (`<div class="navbox">`).
- `references_wrap.py` – sekcja przypisów (`<div class="references-wrap">`).
- `figure.py` – rysunek (`<figure>`).

## Granice odpowiedzialności

- Parsery elementarne nie mapują bezpośrednio na rekordy domenowe.
- Parsery sekcji składają strukturę i przekazują dane niżej/wyżej, bez logiki domenowej.
- Mappery domenowe tabel wiki (`WikiTableBaseParser`) realizują mapowanie kolumn i normalizację
  rekordów — przyjmują `dict` (dane po parsowaniu HTML), nie `Tag`.
- Moduły domenowe korzystają z kontraktów parserów (`Protocol`), nie z odwrotnych zależności
  parser → domena.

## Konwencje nazewnicze

| Suffix klasy | Wejście | Wyjście | Klasa bazowa |
|---|---|---|---|
| `*TableParser` (HTML) | `Tag` (`<table>`) | `dict` | `WikiTableHtmlParser` |
| `*TableParser` (domain) | `dict` | `dict` | `WikiTableBaseParser` |
| `*ListParser` | `Tag` (`<ul>`/`<ol>`) | `dict` | `ListParser` / `WikiListParser` |
| `*SectionParser` | `BeautifulSoup` | `SectionParseResult` | `SectionParser` (Protocol) |
| `*SectionParser` (nested) | `Tag` | `dict` | `NestedWikiSectionParser` |
| `*InfoboxParser` | `Tag` (`<table class="infobox">`) | `dict` | `WikiInfoboxElementParserBase` |
