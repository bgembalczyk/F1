# Scraper extension guide

Dokument opisuje **docelowy kontrakt rozszerzania scraperów**: obowiązkowe hooki, dozwolone punkty rozszerzeń i antywzorce, których należy unikać.

> Zakres: nowe moduły list scraper / single scraper tworzone na bazie `scrapers/templates/`.

## 1. Kontrakt obowiązkowy

### 1.1 List scraper (tabelaryczny)

Nowy list scraper musi zachować trzy elementy kontraktu:

1. `SCRAPER_TEMPLATE_CONFIG` (spójny kontrakt konfiguracji modułu):
   - `domain`
   - `source_url`
   - `section_id`
   - `expected_headers`
2. `schema_columns` (kolumny schema DSL).
3. `CONFIG` budowane przez `build_scraper_config(...)`.

Minimalny punkt wejścia implementacyjnego:

- dziedziczenie po `F1TableScraper`,
- ustawienie `options_domain` oraz `options_profile`,
- podpięcie `record_factory` i schema DSL w `CONFIG`.

### 1.2 Single scraper (artykuł pojedynczy)

Nowy single scraper musi implementować wszystkie hooki bazowe `SingleWikiArticleScraperBase`:

1. `_build_infobox_payload(self, soup) -> InfoboxPayloadDTO`
2. `_build_tables_payload(self, soup) -> TablesPayloadDTO`
3. `_build_sections_payload(self, soup) -> SectionsPayloadDTO`
4. `_assemble_record(..., infobox_payload, tables_payload, sections_payload) -> dict[str, Any]`

Dodatkowo moduł zachowuje kontrakt `SCRAPER_TEMPLATE_CONFIG` (co najmniej `domain`, `base_url`).

## 2. Dopuszczalne punkty rozszerzeń

Rozszerzenia powinny być wykonywane **warstwowo**, bez mieszania odpowiedzialności:

- **Parser / adapter techniczny**: selektory HTML, ekstrakcja fragmentów DOM, normalizacja techniczna.
- **Normalizer**: czyszczenie wartości, standaryzacja struktur pomocniczych.
- **Assembler / serwis domenowy**: decyzje biznesowe, mapowania domenowe, filtrowanie rekordów.
- **Exporter**: serializacja i zapis.

### 2.1 Hooki lifecycle i nazewnictwo

Nowe hooki (jeżeli naprawdę wymagane) muszą stosować konwencję:

- `before_<akcja>`
- `after_<akcja>`
- `on_<zdarzenie>`
- `validate_<kontekst>`

Nie dodajemy nowych aliasów znaczeniowo równoważnych (`pre_*`, `post_*`), poza przypadkami legacy-kompatybilności.

### 2.2 Rozszerzenia preferowane w list scraperze

- Rozszerzaj `schema_columns` przez DSL (`column(...)`, dedykowane parsery kolumn).
- Rozszerzaj `CONFIG` przez parametry `build_scraper_config(...)`, zamiast ręcznego składania niestandardowych obiektów config.
- Dodatkowe reguły domenowe przenoś do walidatora/assemblera zamiast osadzać je w parserze tabeli.

### 2.3 Rozszerzenia preferowane w single scraperze

- Każdy hook `_build_*_payload` niech buduje tylko swój fragment danych (infobox / tables / sections).
- Łączenie danych i decyzje domenowe wykonuj w `_assemble_record(...)` lub dedykowanym serwisie domenowym wywoływanym przez assembler.
- Wspólne zachowania wynoś do `scrapers/base/*` tylko gdy są realnie wielodomenowe.

## 3. Antywzorce (czego nie robić)

1. **Brak kompletu hooków w single scraperze** (np. pominięcie `_build_sections_payload`) i obchodzenie kontraktu przez logikę inline.
2. **Mieszanie warstw**:
   - logika biznesowa w parserze HTML,
   - bezpośrednie selektory DOM w assemblerze domenowym.
3. **Rozjeżdżanie kontraktu list scrapera**:
   - brak `SCRAPER_TEMPLATE_CONFIG`,
   - `CONFIG` bez `build_scraper_config(...)`,
   - schema tabeli budowana ad-hoc poza DSL.
4. **Niespójne nazewnictwo hooków** (`pre_*`, `post_*`, `handle_*`) bez wymogu kompatybilności legacy.
5. **Duplikacja między domenami** zamiast wyciągnięcia wspólnego helpera/adaptora.
6. **Zostawianie placeholderów `TODO`** w nowym scraperze.

## 4. Minimalne przykłady zgodne z kontraktem

### 4.1 Minimalny list scraper

```python
from dataclasses import dataclass
from typing import ClassVar

from scrapers.base.records import record_from_mapping
from scrapers.base.table.config import ScraperConfig, build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.scraper import F1TableScraper


@dataclass(frozen=True, slots=True)
class ExampleListConfig:
    domain: str
    source_url: str
    section_id: str | None
    expected_headers: tuple[str, ...]


SCRAPER_TEMPLATE_CONFIG = ExampleListConfig(
    domain="example",
    source_url="https://en.wikipedia.org/wiki/Example",
    section_id=None,
    expected_headers=("Name",),
)


class ExampleListScraper(F1TableScraper):
    options_domain: ClassVar[str | None] = SCRAPER_TEMPLATE_CONFIG.domain
    options_profile: ClassVar[str | None] = "list_scraper"

    schema_columns = [
        column("Name", "name"),
    ]

    CONFIG: ClassVar[ScraperConfig] = build_scraper_config(
        url=SCRAPER_TEMPLATE_CONFIG.source_url,
        section_id=SCRAPER_TEMPLATE_CONFIG.section_id,
        expected_headers=list(SCRAPER_TEMPLATE_CONFIG.expected_headers),
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=record_from_mapping,
    )
```

### 4.2 Minimalny single scraper

```python
from dataclasses import dataclass
from typing import Any, ClassVar

from bs4 import BeautifulSoup

from scrapers.base.single_wiki_article import (
    InfoboxPayloadDTO,
    SectionsPayloadDTO,
    SingleWikiArticleScraperBase,
    TablesPayloadDTO,
)


@dataclass(frozen=True, slots=True)
class ExampleSingleConfig:
    domain: str
    base_url: str


SCRAPER_TEMPLATE_CONFIG = ExampleSingleConfig(
    domain="example",
    base_url="https://en.wikipedia.org/wiki/Example",
)


class ExampleSingleScraper(SingleWikiArticleScraperBase):
    options_domain: ClassVar[str | None] = SCRAPER_TEMPLATE_CONFIG.domain
    options_profile: ClassVar[str] = "article_strict"

    def _build_infobox_payload(self, soup: BeautifulSoup) -> InfoboxPayloadDTO:
        _ = soup
        return InfoboxPayloadDTO(data={})

    def _build_tables_payload(self, soup: BeautifulSoup) -> TablesPayloadDTO:
        _ = soup
        return TablesPayloadDTO(data={})

    def _build_sections_payload(self, soup: BeautifulSoup) -> SectionsPayloadDTO:
        _ = soup
        return SectionsPayloadDTO(data={})

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: InfoboxPayloadDTO,
        tables_payload: TablesPayloadDTO,
        sections_payload: SectionsPayloadDTO,
    ) -> dict[str, Any]:
        _ = soup
        return {
            "url": self.url,
            "infobox": infobox_payload.data,
            "tables": tables_payload.data,
            "sections": sections_payload.data,
        }
```

## 5. Checklista review dla nowego scrapera

- [ ] Użyto szablonu z `scrapers/templates/`.
- [ ] Zachowano kontrakt `SCRAPER_TEMPLATE_CONFIG`.
- [ ] Single scraper implementuje komplet 4 hooków `_build_*` + `_assemble_record`.
- [ ] List scraper używa schema DSL i `build_scraper_config(...)`.
- [ ] Brak placeholderów `TODO`.
- [ ] Brak mieszania warstw technicznych i domenowych.
- [ ] Nazwy nowych modułów są semantyczne (`Service`/`Factory`/`Runner`/`Adapter`/`EntryPoint`) lub jednoznacznie celowe technicznie.
- [ ] Nie dodano nowego `helpers.py` bez udokumentowanego wyjątku (ADR/uzasadnienie w PR).

## 6. Powiązane dokumenty

- `scrapers/README.md` (workflow tworzenia nowych scraperów)
- `docs/MODULE_BOUNDARIES.md` (granice modułów i checklista PR)
- `docs/CHANGES_CHECKLIST.md` (merge-gate i governance)
- `docs/adr/0004-hook-naming-conventions.md` (konwencja nazewnictwa hooków)
- `docs/architecture/module-naming-standard.md` (standard nazewnictwa ról i modułów)
