# Parser Hierarchy — Dependency Diagram & Migration Map

## 1. Docelowa hierarchia dziedziczenia parserów

```
ParserABC[In, Out]                          ← warstwa 0 – kontrakt bazowy
├── HtmlTagParserABC[TagOut]                ← warstwa 1a – parser Tag (bs4)
│   └── HtmlElementParserABC[TagOut]        ← warstwa 1b – parser elementu HTML
│       ├── ListElementParserABC[Out]
│       ├── TableElementParserABC[Out]
│       ├── InfoboxElementParserABC[Out]
│       ├── SectionElementParserABC[Out]
│       ├── NavboxElementParserABC[Out]
│       ├── ReferencesElementParserABC[Out]
│       ├── ParagraphElementParserABC[Out]
│       └── FigureElementParserABC[Out]
│           │
│           ├── WikiTableParserABC          ← warstwa 2 – Wiki element ABCs
│           ├── WikiListParserABC
│           ├── WikiSectionParserABC
│           ├── WikiInfoboxParserABC
│           ├── WikiNavboxParserABC
│           └── WikiFigureParserABC
│
└── HtmlSoupParserABC[SoupOut]              ← warstwa 1c – parser BeautifulSoup
    └── SectionParserABC                   ← kontrakt sekcyjny (soup-based)
        ├── NestedSectionParserABC
        │   ├── SubSectionParserABC
        │   └── SubSubSectionParserABC
        └── SectionStructureParserABC
```

### Dodatkowe gałęzie

```
ParserABC[In, Out]
├── InfoboxParserABC                        ← parser całego infoboxu (Tag → dict)
│   └── WikiInfoboxParserABC               (również InfoboxElementParserABC)
└── InfoboxFieldParserABC                  ← parser pojedynczego pola infoboxu
    └── InfoboxFieldParser[Output]         ← runtime base (field/protocol.py)
```

### Mixiny

```
SafeParsingMixin                           ← bezpieczna obsługa wyjątków (_safe_parse)
WikiElementParsingMixin                    ← parse_elements / _parse_element (mixin orkiestratora)
```

---

## 2. Mapowanie kontraktów: stara_baza → nowa_baza

| Stara baza (przed migracją) | Nowa baza (po migracji) | Uwagi |
|---|---|---|
| `Protocol` (typing) | `ABC` (abc) | Zastąp klasą ABC z `@abstractmethod` |
| `ElementParserABC` | `HtmlElementParserABC` | Alias usunięty — używaj wyłącznie `HtmlElementParserABC`. |
| `ListElementParserABC` | `WikiListParserABC` *(dla wiki-parserów)* | Używaj wiki-ABC dla konkretnych wiki-parserów |
| `TableElementParserABC` | `WikiTableParserABC` *(dla wiki-parserów)* | j.w. |
| `InfoboxElementParserABC` | `WikiInfoboxParserABC` *(dla wiki-parserów)* | j.w. |
| `SectionElementParserABC` | `WikiSectionParserABC` *(dla wiki-parserów)* | j.w. |
| `NavboxElementParserABC` | `WikiNavboxParserABC` *(dla wiki-parserów)* | j.w. |
| `FigureElementParserABC` | `WikiFigureParserABC` *(dla wiki-parserów)* | j.w. |
| `TagParserABC` | `HtmlTagParserABC` | `TagParserABC` = alias wstecznej kompatybilności |
| `SoupParserABC` | `HtmlSoupParserABC` | `SoupParserABC` = alias wstecznej kompatybilności |

---

## 3. Pakiet kontraktów (`scrapers/parsers/contracts/`)

Stabilne punkty re-eksportu — importuj **stąd**, nie z modułów implementacyjnych:

| Moduł | Eksportuje |
|---|---|
| `contracts/__init__.py` | Wszystkie poniższe symbole |
| `contracts/html_element_parser_abc.py` | `HtmlElementParserABC` |
| `contracts/soup_parser_abc.py` | `TagParserABC` |
| `contracts/mapper_abc.py` | `MapperABC` |
| `contracts/wiki_section_parser_abc.py` | `WikiSectionParserABC` |
| `contracts/wiki_elements.py` | `WikiTableParserABC`, `WikiListParserABC`, `WikiSectionParserABC`, `WikiInfoboxParserABC`, `WikiNavboxParserABC`, `WikiFigureParserABC` |

---

## 4. Rejestr parserów domenowych (`registry.py`)

Rejestr używa wiki-specyficznych ABCs jako baz dla wpisów domenowych:

| Typ elementu | Baza w rejestrze | Uzasadnienie |
|---|---|---|
| `"table"` | `WikiListParserABC` | Tabele to ustrukturyzowane dane (jak listy) |
| `"list"` | `WikiListParserABC` | Listy Wikipedii |
| `"section"` | `WikiSectionParserABC` | Sekcje artykułów Wikipedii |
| `"infobox"` | `WikiSectionParserABC` | Infoboxy to element struktury sekcji |

---

## 5. Zasady migracji

1. **Nie twórz nowych Protocol klas dla parserów** — używaj `ABC` z `@abstractmethod`.
2. **Nowe parsery wiki** — dziedzicz po odpowiednim `Wiki*ParserABC`.
3. **Nowe parsery HTML ogólne** — dziedzicz po `HtmlElementParserABC` lub specjalistycznym `*ElementParserABC`.
4. **Importuj kontrakty** z `scrapers.parsers.contracts.*`, nie z modułów implementacyjnych.
5. **Protokoły** w `scrapers/protocols/` (capabilities, data_frame_formatter itp.) pozostają jako `Protocol` — dotyczą scraper-capabilities, nie parser-contracts.


## 6. Usunięte moduły aliasujące (re-export only)

Poniższe ścieżki zostały usunięte i nie są już wspierane:

- `scrapers/wiki/parsers/*` (moduły re-eksportujące parsery),
- `scrapers/wiki/parsers/elements/*` (re-eksporty parserów elementów),
- `scrapers/wiki/parsers/sections/*` (re-eksporty parserów sekcyjnych),
- `scrapers/parsers/section/sublevels/{sub_section,sub_sub_section,sub_sub_sub_section}.py`.

Używaj importów kanonicznych z `scrapers.parsers.contracts.*` (kontrakty) albo bezpośrednio
z modułów implementacyjnych (`scrapers.parsers.wiki.*`, `scrapers.parsers.section.*`).


## 7. Strict element pipeline (wdrożone)

Parsery elementowe są teraz spięte sztywnym łańcuchem odpowiedzialności:

1. `Element parser (HTML -> payload)`
2. `Classifier (opcjonalny)`
3. `Mapper/Factory (payload -> WikiParsedPayload / rekord domenowy)`

Implementacja runtime dla wiki-elementów:

- `scrapers/parsers/wiki/element_dispatcher.py` – deleguje tylko parse + uruchamia factory,
- `scrapers/parsers/wiki/element_payload_factory.py` – classifier + mapper/factory,
- `scrapers/parsers/wiki/element_registry.py` – wybór parsera wyłącznie po `element_type` + context (`domain`, `section_id`, `section_profile`).

## 8. Rozszerzenie kontraktów sekcyjnych poza tabele

Wzorzec z `scrapers/parsers/section/table/contracts.py` został rozszerzony na:

- `scrapers/parsers/section/list/contracts.py`,
- `scrapers/parsers/section/text/contracts.py`,
- `scrapers/parsers/section/infobox/contracts.py`.

Każdy moduł definiuje analogiczne role: `*HtmlParserABC`, `*ClassifierABC`, `*RecordMapperABC`.

## 9. Granice parser vs domena

Parsery elementowe nie zawierają reguł biznesowych domeny.
Transformacje domenowe pozostają w mapperach/factory (`*mapper*`, `services`, `domain_*`).
