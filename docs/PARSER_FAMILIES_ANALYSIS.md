# Parser Families Analysis (final)

## Finalny, 3‑poziomowy podział kontraktów

```text
ParserABC[In, Out]
├── HtmlTagParserABC[Out]
│   ├── TableHtmlParserABC[Out]
│   ├── ListHtmlParserABC[Out]
│   ├── InfoboxHtmlParserABC[Out]
│   ├── NavboxHtmlParserABC[Out]
│   └── ParagraphHtmlParserABC[Out]
└── HtmlSoupParserABC[Out]
    └── SectionHtmlParserABC[Out]
```

Dla kompatybilności utrzymane są aliasy (`ElementParserABC`, `*ElementParserABC`), ale nowe implementacje powinny być oparte o rodziny `*HtmlParserABC`.【F:scrapers/parsers/element_parser_abc.py†L1-L121】

---

## Reguły kontraktowe

1. Klasa z sufiksem `*Parser` musi implementować publiczne `parse(...)` i realizować kontrakt parsera (`ParserABC` albo wyspecjalizowaną rodzinę HTML).【F:scrapers/parsers/parser_abc.py†L1-L16】【F:scrapers/parsers/tag_parser_abc.py†L1-L19】【F:scrapers/parsers/soup_parser_abc.py†L1-L22】
2. Dla rodzin HTML wejściem jest HTML:
   - `Tag` dla `Table/List/Infobox/Navbox/Paragraph`,
   - `BeautifulSoup` (lub wejście sekcyjne kompatybilne z HTML) dla `Section`.
3. Klasy operujące na strukturach pośrednich (`dict`, `list[dict]`) nie powinny używać sufiksu `Parser` — używamy `*Extractor` (wydobycie) lub `*Mapper` (mapowanie domenowe).

---

## Parser vs Extractor vs Mapper

- **Parser**
  - odpowiedzialność: parsowanie surowego wejścia (HTML / tekst) do ustrukturyzowanego payloadu,
  - API: `parse(raw) -> parsed`.

- **Extractor**
  - odpowiedzialność: wydobycie informacji z *już sparsowanych* struktur pośrednich,
  - API zwykle `extract(...)` lub domenowe metody pomocnicze,
  - wejście: zwykle `dict` / `list[dict]` / DTO.

- **Mapper**
  - odpowiedzialność: mapowanie payloadu pośredniego na rekord domenowy,
  - API: `map(raw) -> mapped` (ew. z dodatkowymi kontekstami).

---

## Rozdział `section/table/**` (parser HTML / classifier / mapper)

W warstwie parsowania tabel sekcji zostały jawnie wydzielone trzy role:

1. **Parser HTML tabel sekcji** – `SectionTablesHtmlParserABC` + domyślny `ArticleSectionTablesHtmlParser` (`BeautifulSoup -> list[dict]`).【F:scrapers/parsers/section/table/contracts.py†L1-L28】【F:scrapers/parsers/section/table/base.py†L1-L40】
2. **Klasyfikator tabel** – `SectionTableClassifierABC` oraz implementacje domenowe (np. `DriverResultsSectionTableClassifier`, `CircuitLapRecordsTableClassifier`).【F:scrapers/parsers/section/table/contracts.py†L30-L36】【F:scrapers/parsers/section/table/driver_results.py†L1-L33】【F:scrapers/parsers/section/table/circuit/lap_records.py†L1-L37】
3. **Mapper rekordów** – `SectionTableRecordMapperABC` oraz implementacje domenowe (np. `DriverResultsTableRecordMapper`, `CircuitEventsTableRecordMapper`, `CircuitLapRecordsTableRecordMapper`).【F:scrapers/parsers/section/table/contracts.py†L38-L51】【F:scrapers/parsers/section/table/driver_results.py†L35-L58】【F:scrapers/parsers/section/table/circuit/events.py†L1-L18】【F:scrapers/parsers/section/table/circuit/lap_records.py†L39-L67】

Orkiestrację tych trzech kroków realizuje `TableSectionParser`.【F:scrapers/parsers/section/table/base.py†L68-L194】
