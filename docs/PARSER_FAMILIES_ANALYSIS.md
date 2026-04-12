# Parser Families Analysis

Analiza klas `*Parser` w katalogu `scrapers/parsers/` oraz poza nim.

---

## Tabela klas *Parser

| Klasa | Moduł | Aktualna baza | Typ wejścia | Typ wyjścia | Parsuje HTML Wikipedii | Docelowa rodzina |
|---|---|---|---|---|---|---|
| `HtmlTableParser` | `scrapers.parsers.html_table` | `HtmlSoupParserABC` | `BeautifulSoup` | `list[dict]` | Nie (ogólny HTML) | **Table** |
| `WikiTableParser` | `scrapers.parsers.wiki.table.__init__` | `WikiTableHtmlParser` | `Tag` | `WikiTableData` | Tak | **Table** |
| `WikiTableBaseParser` | `scrapers.parsers.wiki.table.base` | `TableParserABC` | `dict` | `dict` | Nie (dane już sparsowane) | **Table** |
| `WikiTableHtmlParser` | `scrapers.parsers.wiki.table.html` | `WikiTableParserABC` | `Tag` | `WikiTableData` | Tak | **Table** |
| `F1StandingsTableParser` | `scrapers.parsers.section.standings.f1_table` | `HtmlTagParserABC` | `Tag` | `list[dict]` | Tak | **Table** |
| `DriverOrderedTableParser` | `scrapers.parsers.table.base_ordered` | `WikiTableBaseMapper` | `dict` | `list[dict]` | Nie (mapuje dane) | **Table** |
| `DriversListTableMapper` | `scrapers.parsers.drivers_list_table_mapper` | `DriverOrderedTableMapper` | `dict` | `list[dict]` | Nie | **Table** |
| `WikiListParser` | `scrapers.parsers.wiki.base` | `HtmlTagParserABC` | `Tag` | `WikiRecords` | Tak (ABC) | **List** |
| `WikiListElementParser` | `scrapers.parsers.wiki.element_list` | `WikiListParserABC` | `Tag` | `WikiListData` | Tak | **List** |
| `ListElementParser` | `scrapers.parsers.list_element_parser` | `WikiListParserABC, ListElementParserABC` | `Tag` | `ListElementData` | Tak | **List** |
| `IndianapolisOnlyListParser` | `scrapers.parsers.list_element.engine_manufacturers_list` | `ListElementParser` | `Tag` | `dict` | Tak | **List** |
| `IndianapolisConstructorsListParser` | `scrapers.parsers.list_element.indianapolis_constructors` | `ListElementParser` | `Tag` | `dict` | Tak | **List** |
| `PrivateerTeamsListParser` | `scrapers.parsers.privateer_teams_list` | `WikiListElementParser` | `Tag` | `dict` | Tak | **List** |
| `BaseSectionParser` | `scrapers.parsers.wiki.base_section_parser` | `WikiSectionParserABC` | `BeautifulSoup` | `SectionParseResult` | Tak (ABC) | **Section** |
| `NestedWikiSectionParser` | `scrapers.parsers.wiki.nested_wiki` | `BaseNestedSectionParser` | `Tag\|list[Tag]` | `dict` | Tak | **Section** |
| `RecursiveSectionParser` | `scrapers.parsers.wiki.recursive` | `WikiParser` | `Tag\|list[Tag]` | `dict` | Tak (infrastruktura) | **Section** |
| `TableSectionParser` | `scrapers.parsers.section.table.base` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section/Table** |
| `CircuitEventsSectionParser` | `scrapers.parsers.section.table.circuit.events` | `TableSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `CircuitLapRecordsSectionParser` | `scrapers.parsers.section.table.circuit.lap_records` | `TableSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `ConstructorTablesSectionParser` | `scrapers.parsers.section.table.constructor.base` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `ConstructorHistorySectionParser` | `scrapers.parsers.section.table.constructor.history` | `ConstructorTablesSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `ConstructorChampionshipResultsSectionParser` | `scrapers.parsers.section.table.constructor.results.championship` | `ConstructorTablesSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `ConstructorCompleteF1ResultsSectionParser` | `scrapers.parsers.section.table.constructor.results.complete_f1` | `ConstructorTablesSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `DriverResultsSectionParser` | `scrapers.parsers.section.table.driver_results` | `TableSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `SeasonResultsSectionParser` | `scrapers.parsers.section.results.season` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `BaseDriverResultsSectionParser` | `scrapers.parsers.section.results.base_drivers_results` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `SeasonCalendarSectionParser` | `scrapers.parsers.section.season.calendar` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `SeasonDriversStandingsSectionParser` | `scrapers.parsers.section.standings.season.drivers` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `SeasonConstructorsStandingsSectionParser` | `scrapers.parsers.section.standings.season.constructors` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `CircuitsListSectionParser` | `scrapers.parsers.section.circuit.list` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `ConstructorsSectionParser` | `scrapers.parsers.section.constructors.base` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `GrandPrixByYearSectionParser` | `scrapers.parsers.section.grand_prix.by_year` | `BaseSectionParser` | `BeautifulSoup` | `SectionParseResult` | Tak | **Section** |
| `HistorySectionParser` | `scrapers.parsers.wiki.engine_regulation` | `BaseNestedSectionParser` | `Tag\|list[Tag]` | `dict` | Tak | **Section** |
| `CurrentRulesSectionParser` | `scrapers.parsers.wiki.engine_restrictions` | `BaseNestedSectionParser` | `Tag\|list[Tag]` | `dict` | Tak | **Section** |
| `WikiInfoboxParser` | `scrapers.parsers.wiki.infobox` | `WikiInfoboxHtmlParser` | `Tag` | `dict` | Tak | **Infobox** |
| `WikiInfoboxHtmlParser` | `scrapers.parsers.infobox.wiki_html` | `WikiInfoboxParserABC` | `BeautifulSoup` | `dict` | Tak | **Infobox** |
| `WikiInfoboxElementParser` | `scrapers.parsers.wiki.element_infobox` | `WikiInfoboxParserABC` | `Tag` | `WikiInfoboxData` | Tak | **Infobox** |
| `InfoboxFieldParser` | `scrapers.parsers.infobox.field.protocol` | `InfoboxFieldParserABC` | `dict` | `Any` | Nie (przetwarza dict) | **Infobox** |
| `WikiNavboxElementParser` | `scrapers.parsers.wiki.element_navbox` | `WikiNavboxParserABC` | `Tag` | `WikiNavboxData` | Tak | **Navbox** |
| `WikiParagraphParser` | `scrapers.parsers.wiki.paragraph` | `ParagraphElementParser` | `Tag` | `ParagraphElementData` | Tak | **Paragraph** |
| `WikiParagraphElementParser` | `scrapers.parsers.wiki.element_paragraph` | `ParagraphElementParser` | `Tag` | `ParagraphElementData` | Tak | **Paragraph** |
| `ParagraphElementParser` | `scrapers.parsers.paragraph_element_parser` | `BaseHtmlElementParser, ParagraphElementParserABC` | `Tag` | `ParagraphElementData` | Tak | **Paragraph** |
| `SeasonCalendarParser` | `scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.calendar` | `BaseSeasonParser` | `BeautifulSoup` | `list[dict]` | Tak | **Table** |
| `CancelledRoundsParser` | `scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.cancelled_rounds` | `BaseSeasonParser` | `BeautifulSoup` | `list[dict]` | Tak | **Table** |
| `SeasonEntriesParser` | `scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.entries` | `BaseSeasonParser` | `BeautifulSoup` | `list[dict]` | Tak | **Table** |
| `SeasonResultsParser` | `scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.results` | `BaseSeasonParser` | `BeautifulSoup` | `list[dict]` | Tak | **Table** |
| `SponsorPartsParser` | `scrapers.parsers.liveries.sponsorship.parts` | `ParserABC` | `str` | `list[tuple]` | Nie (parser tekstowy) | **Text/Utility** |
| ~~`CircuitGeoParser`~~ → **`CircuitGeoExtractor`** | `scrapers.parsers.infobox.text_utils.circuit.geo` | `InfoboxTextUtils` | `dict` | `dict` | Nie (przetwarza dane) | **Text/Utility** |
| ~~`CircuitHistoryParser`~~ → **`CircuitHistoryExtractor`** | `scrapers.parsers.infobox.text_utils.circuit.history` | `InfoboxTextUtils` | `dict` | `dict` | Nie | **Text/Utility** |
| ~~`CircuitSpecsParser`~~ → **`CircuitSpecsExtractor`** | `scrapers.parsers.infobox.text_utils.circuit.specs` | `InfoboxTextUtils` | `dict` | `dict` | Nie | **Text/Utility** |
| ~~`CircuitLapRecordParser`~~ → **`CircuitLapRecordExtractor`** | `scrapers.parsers.infobox.text_utils.circuit.lap_record` | `CircuitTextProcessing` | `dict` | `dict` | Nie | **Text/Utility** |
| ~~`CircuitLayoutsParser`~~ → **`CircuitLayoutsExtractor`** | `scrapers.parsers.infobox.text_utils.circuit.layouts` | `SafeParsingMixin` | `list` | `list[dict]` | Nie | **Text/Utility** |
| ~~`CircuitEntityParser`~~ → **`CircuitEntityExtractor`** | `scrapers.parsers.infobox.text_utils.circuit.text_processing.entity.base` | `CircuitTextProcessing` | `dict` | `dict` | Nie | **Text/Utility** |
| ~~`CircuitAdditionalInfoParser`~~ → **`CircuitAdditionalInfoExtractor`** | `scrapers.parsers.infobox.text_utils.circuit.text_processing.entity.additional_info` | `CircuitEntityExtractor` | `dict` | `dict` | Nie | **Text/Utility** |
| `SponsorshipSectionParser` | `scrapers.parsers.wiki.sponsorship` | `WikiSectionParserBase` | `BeautifulSoup` | `list[dict]` | Tak | **Section** |
| `TeamLiveriesSectionParser` | `scrapers.parsers.team_liveries_section` | `WikiSectionParserBase` | `BeautifulSoup` | `list[dict]` | Tak | **Section** |

---

## Rodziny parserów

### Table (parsery tabel HTML)
Klasy parsujące tabele HTML — zarówno z Wikipedii, jak i ogólne:
- `HtmlTableParser` — ogólny parser tabel HTML (nie wiki-specyficzny)
- `WikiTableParser`, `WikiTableHtmlParser`, `WikiTableBaseParser`
- `F1StandingsTableParser` — parser klasyfikacji F1
- `SeasonCalendarParser`, `CancelledRoundsParser`, `SeasonEntriesParser`, `SeasonResultsParser` i inne `Season*Parser` z `seasons_wiki_table_element_parser_base/` — parsery sezonowych tabel Wikipedii

### List (parsery list HTML)
Klasy parsujące listy `<ul>`/`<ol>`:
- `WikiListParser` (ABC), `WikiListElementParser`
- `ListElementParser`, `IndianapolisOnlyListParser`, `IndianapolisConstructorsListParser`
- `PrivateerTeamsListParser`

### Section (parsery sekcji artykułów)
Klasy parsujące sekcje artykułów Wikipedii:
- `BaseSectionParser` (kanoniczny base), `NestedWikiSectionParser`, `RecursiveSectionParser`
- `TableSectionParser` i jego podklasy (`CircuitEventsSectionParser`, etc.)
- `SeasonResultsSectionParser`, `SeasonCalendarSectionParser`, `SeasonDriversStandingsSectionParser`, etc.
- `SponsorshipSectionParser`, `TeamLiveriesSectionParser` (liveries — inny interface)

### Infobox (parsery infobox)
- `WikiInfoboxParser`, `WikiInfoboxHtmlParser`, `WikiInfoboxElementParser`
- `InfoboxFieldParser` — parser pojedynczych pól infobox (dict → Any)

### Navbox (parsery navbox)
- `WikiNavboxElementParser`

### Paragraph (parsery paragrafów)
- `WikiParagraphParser`, `WikiParagraphElementParser`, `ParagraphElementParser`

### Text/Utility (pomocnicze przetwarzanie tekstu — NIE parsery HTML)
Klasy, które przetwarzają dane w formacie `dict`/`str`, nie parsują HTML:
- **`CircuitGeoExtractor`** (wcześniej: `CircuitGeoParser`)
- **`CircuitHistoryExtractor`** (wcześniej: `CircuitHistoryParser`)
- **`CircuitSpecsExtractor`** (wcześniej: `CircuitSpecsParser`)
- **`CircuitLapRecordExtractor`** (wcześniej: `CircuitLapRecordParser`)
- **`CircuitLayoutsExtractor`** (wcześniej: `CircuitLayoutsParser`)
- **`CircuitEntityExtractor`** (wcześniej: `CircuitEntityParser`)
- **`CircuitAdditionalInfoExtractor`** (wcześniej: `CircuitAdditionalInfoParser`)
- `SponsorPartsParser` — parser tekstu (str → list[tuple]), nie HTML

---

## Klasy błędnie nazwane jako *Parser — zrealizowane renamingi

Poniższe klasy zostały przemianowane, ponieważ nie implementowały kontraktu parserowcego
(`ParserABC` / `WikiParser` / etc.) i nie przetwarzały HTML Wikipedii. Zamiast tego operowały
na słownikach (`dict`) lub tekstach (`str`) będących już sparsowanymi danymi infobox.

| Stara nazwa | Nowa nazwa | Powód |
|---|---|---|
| `CircuitGeoParser` | `CircuitGeoExtractor` | Dziedziczy po `InfoboxTextUtils`, wejście `dict` |
| `CircuitHistoryParser` | `CircuitHistoryExtractor` | Dziedziczy po `InfoboxTextUtils`, wejście `dict` |
| `CircuitSpecsParser` | `CircuitSpecsExtractor` | Dziedziczy po `InfoboxTextUtils`, wejście `dict` |
| `CircuitLapRecordParser` | `CircuitLapRecordExtractor` | Dziedziczy po `CircuitTextProcessing`, wejście `dict` |
| `CircuitLayoutsParser` | `CircuitLayoutsExtractor` | Dziedziczy po `SafeParsingMixin`, wejście `list` |
| `CircuitEntityParser` | `CircuitEntityExtractor` | Dziedziczy po `CircuitTextProcessing`, wejście `dict` |
| `CircuitAdditionalInfoParser` | `CircuitAdditionalInfoExtractor` | Dziedziczy po `CircuitEntityExtractor`, wejście `dict` |

---

## Konwencja nazewnictwa

- `*Parser` — klasa implementująca kontrakt parsera (`ParserABC` lub pochodna) z metodą `parse()`
- `*Extractor` — klasa wyciągająca/transformująca dane z już sparsowanych struktur (dict/str)
- `*Mapper` — klasa mapująca kolumny tabel (wiki table domain mapping)
- `*SectionParser` — klasa parsująca sekcje artykułów Wikipedii (dziedziczy po `BaseSectionParser` lub `NestedWikiSectionParser`)
- `*TableParser` — klasa parsująca tabele Wikipedii (dziedziczy po `WikiTableBaseMapper`, `WikiTableHtmlParser` lub `WikiTableElementParserBase`)
- `*ListParser` — klasa parsująca listy HTML (dziedziczy po `WikiListParser` lub `WikiListParserABC`)
