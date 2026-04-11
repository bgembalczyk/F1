# Wiki parsers – architektura warstw

Ten katalog utrzymuje parsery odpowiedzialne za ekstrakcję treści z HTML-a Wikipedii.

## Ustalona hierarchia

Parsery są podzielone na cztery warstwy odpowiadające elementom HTML Wikipedii:

1. **HTML Element Parser** (`scrapers/parsers/html_elements/`)
   - odpowiedzialność: parsuje pojedynczy `bs4.Tag` do prostego słownika,
   - klasa bazowa: `BaseHtmlElementParser[T]` (dla `Tag`) lub `BaseHtmlSectionParser[T]` (dla `BeautifulSoup`),
   - brak logiki domenowej ani zależności od wiki-specyficznych klas.

2. **Wiki Element Parser** (`scrapers/parsers/wiki/`)
   - odpowiedzialność: parsuje konkretny element HTML Wikipedii (`Tag`) do struktury danych,
   - klasa bazowa: `WikiParser[Tag, OutputT]`,
   - rodziny elementów: nagłówek (`header`), paragraf (`paragraph`), lista (`list`), tabela wikitable
     (`table/wiki/table.py`), infobox (`infobox`), navbox (`navbox`), przypisy (`references_wrap`),
     rysunek (`figure`).

3. **Structure Parser** (`scrapers/parsers/section/`)
   - odpowiedzialność: kompozycja sekcji/podsekcji i nawigacja po nagłówkach h2–h5,
   - kontrakt: `SectionParser` (dla parserów przyjmujących `BeautifulSoup`, zwracających
     `SectionParseResult`) lub `NestedWikiSectionParser` (dla hierarchicznych parserów sekcji
     przyjmujących `Tag` i zwracających `dict`),
   - parsery sekcji dobierają zestaw parserów elementarnych przez `SectionParserToolbox`.

4. **Table Domain Mapper** (`scrapers/parsers/table/wiki/`)
   - odpowiedzialność: mapowanie już sparsowanych danych tabelarycznych (`dict`) na rekordy domenowe,
   - klasa bazowa: `WikiTableBaseParser` (przyjmuje `dict`, zwraca `dict`),
   - **WAŻNE:** `WikiTableBaseParser` i jego podklasy NIE parsują HTML — przetwarzają dane
     wyjściowe parsera HTML tabeli. Są mapperami domenowymi, nie parserami HTML.

Pełna decyzja architektoniczna: `ADR-0006`.

## Diagram klas (uproszczony)

```
BaseHtmlElementParser[T]
  ├── ListElementParser          → WikiListParser (wiki wrapper)
  ├── TableElementParser         → wraps WikiTableHtmlParser
  ├── InfoboxElementParser       → WikiInfoboxParser
  ├── ParagraphElementParser     → WikiParagraphParser (wiki wrapper)
  ├── NavboxElementParser        → WikiNavboxParser (wiki wrapper)
  └── FigureElementParser        → WikiFigureParser (wiki wrapper)

WikiParser[InputT, OutputT]
  ├── WikiTagParser[OutputT]     → bazowy kontrakt parserów pojedynczego Tag
  ├── WikiTableParser            (<table class="wikitable">)
  ├── WikiInfoboxParser          (<table class="infobox">)
  ├── WikiSectionParser          (kontener sekcji artykułu)
  ├── WikiListParser             (<ul>/<ol>)
  ├── WikiParagraphParser        (<p>)
  ├── WikiNavboxParser           (<div class="navbox">)
  ├── WikiFigureParser           (<figure>)
  ├── HeaderParser               (<header class="mw-body-header">)
  ├── ReferencesWrapParser       (<div class="references-wrap">)
  └── ContentTextParser          (div#content-text)

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
(`SectionParserToolbox`) i delegują parsing HTML do parserów elementów.


## Rodzina parserów elementarnych (`scrapers/parsers/wiki/`)

- `header.py` – nagłówek (`<header class="mw-body-header">`).
- `paragraph.py` – paragraf (`<p>`).
- `list.py` – lista (`<ul>` / `<ol>`).
- `../table/wiki/table.py` – tabela wikitable (`<table class="wikitable">`).
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
