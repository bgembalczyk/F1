# Konwencja nazewnicza parserów

Krótka konwencja dla nowych nazw klas:

- `*ABC` – kontrakty abstrakcyjne (np. `SectionParserABC`).
- `*Mixin` – współdzielone zachowania wielokrotnego dziedziczenia.
- `*Base` – klasy bazowe/abstrakcyjne.
- `*Service` – komponenty usługowe orkiestrujące logikę.
- `*Parser` – parsery wejścia/HTML/sekcji/tabel.

## Rodzina bazowych kontraktów parserów

- `ParserABC` – kontrakt bazowy `parse(input) -> output`.
- `HtmlTagParserABC` – parser wejścia `bs4.Tag`.
- `HtmlSoupParserABC` – parser wejścia `BeautifulSoup`.
- `HtmlElementParserABC` – parser elementów HTML (list/table/infobox/navbox/references/figure).
  - `ElementParserABC` — alias wstecznej kompatybilności dla `HtmlElementParserABC`.
- `SectionParserABC` – parser sekcji (soup-based).

## Hierarchia dziedziczenia

```
ParserABC[In, Out]
├── HtmlTagParserABC[TagOut]
│   └── HtmlElementParserABC[TagOut]        ← warstwa elementów HTML
│       ├── ListElementParserABC
│       ├── TableElementParserABC
│       ├── InfoboxElementParserABC
│       ├── SectionElementParserABC
│       ├── NavboxElementParserABC
│       ├── ReferencesElementParserABC
│       ├── ParagraphElementParserABC
│       └── FigureElementParserABC
│
├── HtmlSoupParserABC[SoupOut]
│   └── SectionParserABC
│       └── SectionStructureParserABC
│
└── Wiki element ABCs (warstwa 2):
    WikiTableParserABC  ← TableElementParserABC[WikiTableData]
    WikiListParserABC   ← ListElementParserABC[WikiListData]
    WikiSectionParserABC
    WikiInfoboxParserABC
    WikiNavboxParserABC
    WikiFigureParserABC
```

Szczegółowy diagram oraz mapa migracji: [`docs/PARSER_HIERARCHY_MIGRATION_MAP.md`](../../docs/PARSER_HIERARCHY_MIGRATION_MAP.md).

## Pakiet kontraktów

Stabilne importy z `scrapers.parsers.contracts.*`:

```python
from scrapers.parsers.contracts.wiki_elements import WikiListParserABC
from scrapers.parsers.contracts.wiki_elements import WikiTableParserABC
from scrapers.parsers.contracts.html_element_parser_abc import HtmlElementParserABC
```

