# Parser Hierarchy Migration Map (po refaktorze)

## 1) Kanoniczna baza kontraktów

```text
ParserABC[In, Out]
├── HtmlTagParserABC[Out]      (bs4.Tag -> Out)
└── HtmlSoupParserABC[Out]     (BeautifulSoup -> Out)
```

Źródło prawdy:
- `scrapers/parsers/parser_abc.py`
- `scrapers/parsers/element_parser_abc.py`

## 2) Rodziny HTML (element_parser_abc)

```text
HtmlTagParserABC[Out]
├── TableHtmlParserABC[Out]
├── ListHtmlParserABC[Out]
├── InfoboxHtmlParserABC[Out]
├── NavboxHtmlParserABC[Out]
├── ParagraphHtmlParserABC[Out]
├── FigureHtmlParserABC[Out]
└── HtmlElementParserABC[Out]   (generyczny tag-based)

HtmlSoupParserABC[Out]
└── SectionHtmlParserABC[Out]
```

Utrzymane aliasy kompatybilności (bez osobnej logiki):
- `ListElementParserABC = ListHtmlParserABC`
- `TableElementParserABC = TableHtmlParserABC`
- `InfoboxElementParserABC = InfoboxHtmlParserABC`
- `SectionElementParserABC = SectionHtmlParserABC`
- `NavboxElementParserABC = NavboxHtmlParserABC`
- `ParagraphElementParserABC = ParagraphHtmlParserABC`
- `FigureElementParserABC = FigureHtmlParserABC`

## 3) Finalne rodziny Wiki (ABC)

Każda rodzina ma jeden docelowy kontrakt:

- `WikiTableParserABC`
- `WikiListParserABC`
- `WikiSectionParserABC`
- `WikiInfoboxParserABC`
- `WikiNavboxParserABC`
- `WikiFigureParserABC`

Lokalizacja:
- `scrapers/parsers/wiki/wiki_*_parser_abc.py`

`section_nodes/*` zostało ograniczone do warstwy kompatybilności (re-export/alias).

## 4) Mapowanie selector -> rodzina parsera Wiki

Mapa jest wymuszana przez:
- `docs/wiki_selector_parser_map.md`
- `scrapers/parsers/wiki/element_registry.py` (`WIKI_SELECTOR_FAMILY_MAP` + walidacja coverage)
- `scrapers/parsers/wiki/element.py` (predykaty zgodne z mapą)

## 5) Usunięte/ograniczone redundancje dziedziczenia

- parsery elementowe (`list/table/infobox/navbox/figure/section`) dziedziczą teraz z **jednej** docelowej gałęzi Wiki ABC,
- parsery sekcyjne legacy (np. `legacy_lists/*`) nie dublują już równolegle baz `SectionParserABC`/`SubSectionParserABC` obok klas runtime,
- `tag_parser_abc.py` i `soup_parser_abc.py` pełnią rolę kompatybilnych re-eksportów.
