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
- `SectionParserABC` – parser sekcji (soup-based).

## Hierarchia dziedziczenia

```
ParserABC[In, Out]
├── HtmlTagParserABC[TagOut]
│   └── HtmlElementParserABC[TagOut]        ← warstwa elementów HTML
│       ├── ListHtmlParserABC
│       ├── TableHtmlParserABC
│       ├── InfoboxHtmlParserABC
│       ├── SectionHtmlParserABC
│       ├── NavboxHtmlParserABC
│       ├── ReferencesElementParserABC
│       ├── ParagraphHtmlParserABC
│       └── FigureHtmlParserABC
│
├── HtmlSoupParserABC[SoupOut]
│   └── SectionParserABC
│
└── Wiki element ABCs (warstwa 2):
    WikiTableParserABC  ← TableHtmlParserABC[WikiTableData]
    WikiListParserABC   ← ListHtmlParserABC[WikiListData]
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


## Kanoniczne importy (po usunięciu aliasów)

- Nie używaj `ElementParserABC` — alias został usunięty.
- Używaj `HtmlElementParserABC` oraz kontraktów z `scrapers.parsers.contracts.*`.
- Nie używaj re-eksportów z `scrapers.wiki.parsers.*` ani `scrapers.parsers.section.sublevels.*`;
  importuj z docelowych modułów parserów.
