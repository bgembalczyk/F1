# Diagramy dziedziczenia klas – F1 Project

Folder zawiera diagramy PlantUML prezentujące **hierarchie dziedziczenia** wszystkich klas projektu,
pogrupowane według rodziny/warstwy.

## Struktura plików

```
docs/uml/inheritance/
├── parsers/
│   ├── 01_parser_abc_core.puml          # ParserABC + kontrakty HTML/Soup + bazy sekcji
│   ├── 02_wiki_html_parsers.puml        # WikiDelegatingHtmlParserBase → WikiXxx*
│   ├── 03_scrapers.puml                 # Hierarchia scraperów (ScraperLifecycleABC…)
│   ├── 04_section_parsers_domain.puml   # Parsery sekcji według domeny
│   ├── 05_table_parsers.puml            # Parsery tabel HTML/wiki
│   ├── 06_wiki_section_nodes.puml       # WikiSectionNodeParserABC i poddrzewa
│   └── 07_misc_parsers.puml             # Pozostałe parsery i asemblery
├── columns/
│   └── 01_columns.puml                  # Hierarchia BaseColumn (66 klas)
├── mappers/
│   └── 01_mappers.puml                  # Hierarchia MapperABC (46 klas)
├── records/
│   ├── 01_record_factories.puml         # Fabryki rekordów
│   ├── 02_record_transformers.puml      # Transformatory rekordów
│   ├── 03_record_validators.puml        # Walidatory rekordów
│   ├── 04_record_strategies.puml        # Strategie podziału i składania rekordów
│   └── 05_value_objects_models.puml     # ValueObject, ValidatedModel, DataContract
├── services/
│   ├── 01_pipeline_services.puml        # Serwisy pipeline'u domenowego
│   └── 02_base_components.puml          # BaseComponent + serwisy ekstrakcji sekcji
├── components/
│   ├── 01_classifiers.puml              # Hierarchia ClassifierABC
│   └── 02_complete_extractors.puml      # Kompletne ekstraktory danych
├── infobox/
│   ├── 01_orchestrators.puml            # Orkiestratory infoboxów i dostawcy bundli
│   └── 02_text_utils.puml               # InfoboxTextUtils – ekstraktory tekstów obwodów
├── infrastructure/
│   ├── 01_errors.puml                   # Hierarchia błędów (ScraperError, RequestError)
│   ├── 02_http_cache.puml               # Klienty HTTP, cache, rate limiter
│   └── 03_layers.puml                   # Warstwy, executory, job runnery
└── misc/
    └── 01_misc_small.puml               # Małe, izolowane hierarchie
```

## Pokrycie

| Pliki | Łączna liczba klas w grafie | Klas w diagramach |
|-------|-----------------------------|-------------------|
| 24    | 568                         | 568 (100%)        |

## Jak przeglądać

**VS Code**: zainstaluj rozszerzenie *PlantUML* i naciśnij `Alt+D` na otwartym pliku `.puml`.

**Online**: skopiuj zawartość pliku na https://www.plantuml.com/plantuml/uml/

## Zasada generowania

Diagramy zostały wygenerowane automatycznie skryptem [`scripts/gen_inheritance_puml.py`](../../../scripts/gen_inheritance_puml.py)
przez analizę AST wszystkich plików `.py` w projekcie (z pominięciem `tests/`, `benchmarks/`, `artifacts/`).
Każda klasa pojawia się **dokładnie w jednym** pliku – brak duplikatów.

Aby odtworzyć / zaktualizować diagramy po zmianach w kodzie:
```bash
python scripts/gen_inheritance_puml.py
```
