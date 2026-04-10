# Problematic families — mapa migracji

## Tabela migracji (stan na 2026-04-10)

| Stara klasa/moduł | Nowa klasa/moduł | Typ zmiany | Status migracji |
|---|---|---|---|
| `scrapers.<domain>.<domain>_services.domain_record.DomainRecordService` (importy per domena: drivers/circuits/constructors/seasons) | `scrapers.services.domain_record.{driver,circuit,constructor,season}.DomainRecordService` | **merge + rename modułu** (konsolidacja do wspólnego katalogu `services/domain_record`) | **W toku (blokujące):** nowa lokalizacja istnieje, ale aktywne importy nadal wskazują stare ścieżki per domena. |
| `scrapers.base.extractors.infobox.InfoboxExtractor` oraz `scrapers.extractors.infobox.InfoboxExtractor` | `scrapers.infobox.extraction.extractor.base.InfoboxExtractor` + `scrapers.infobox.extraction.extractor.protocol.InfoboxExtractor` | **split + rename + deprecate** (rozdzielenie konkretnej implementacji i protokołu) | **W toku (blokujące):** istnieją mieszane importy starego i nowego API. |
| `scrapers.config_table.ScraperConfig` | `scrapers.base.table.config.ScraperConfig` (+ `build_scraper_config`) | **rename modułu** | **W toku (blokujące):** importy kanoniczne są szeroko używane, ale w drzewie kodu brak pliku `scrapers/base/table/config.py`; część modułów wciąż używa `scrapers.config_table`. |
| `scrapers.config.ScraperConfig` (runtime/app config) | wydzielenie do dedykowanego runtime config (np. `RunConfig`) bez kolizji nazwy z table config | **split + deprecate** | **Nierozpoczęta/niejednoznaczna:** nazwa nadal koliduje semantycznie z `ScraperConfig` tabelowym. |

---

## Miejsca użycia do migracji moduł po module

Poniżej celowo tylko **importy i instancjacje**, żeby łatwo planować PR-y etapami.

## 1) `DomainRecordService`

### Importy

- `scrapers/composition_drivers.py`
- `scrapers/circuits_composition.py`
- `scrapers/constructors_composition.py`
- `scrapers/composition_seasons.py`
- `tests/test_single_scraper_components_and_orchestration.py`
- `tests/scrapers/circuits/test_domain_record.py`

### Instancjacje

- `scrapers/composition_drivers.py`
- `scrapers/circuits_composition.py`
- `scrapers/constructors_composition.py`
- `scrapers/composition_seasons.py`
- `tests/test_single_scraper_components_and_orchestration.py`
- `tests/scrapers/circuits/test_domain_record.py`

## 2) `InfoboxExtractor`

### Importy

- `tests/scrapers/base/test_debug_dumps.py`
- `tests/test_extractors.py`
- `scrapers/infobox/extraction/service/strategy.py`
- `scrapers/infobox/extraction/service/circuit.py`
- `scrapers/infobox/parsers/helpers.py`
- `scrapers/infobox/extraction/extractor/circuit.py` (import protokołu)

### Instancjacje

- `tests/scrapers/base/test_debug_dumps.py`
- `tests/test_extractors.py`
- `scrapers/infobox/parsers/helpers.py`
- `scrapers/infobox/extraction/service/circuit.py` (`CircuitInfoboxExtractor()` jako implementacja strategii)

## 3) `ScraperConfig`

### Importy

#### Kanoniczne (docelowe): `scrapers.base.table.config`

- `scrapers/scraper_table.py`
- `scrapers/pipeline_table.py`
- `scrapers/extractors/table.py`
- `scrapers/list_scraper_tyres.py`
- `scrapers/list_scraper_seasons.py`
- `scrapers/standings_scraper_seasons.py`
- `scrapers/fatalities_list_scraper_drivers.py`
- `scrapers/seed_list_scraper_table.py`
- `scrapers/constructors_config_factory.py`
- `scrapers/config_factory_points.py`
- `scrapers/builders_table.py` (TYPE_CHECKING)
- `tests/test_scraper_contract.py`
- `tests/test_table_scraper_options.py`
- `tests/test_table_pipeline.py`
- `tests/test_table_headers.py`
- `tests/test_section_parser_contract.py`
- `tests/test_extractors.py`
- `tests/test_models.py`

#### Legacy/mieszane

- `scrapers/config_table.py` (definicja)
- `scrapers/parsers/section/list/circuits.py`
- `scrapers/parsers/section/table/base.py`
- `scrapers/parsers/section/table/results/driver.py`
- `scrapers/parsers/section/sponsorship.py`
- `scrapers/parsers/section/grand_prix/by_year.py`
- `scrapers/parsers/seasons/table.py`
- `scrapers/parsers/seasons/cancelled_rounds.py`
- `scrapers/config.py` (inny `ScraperConfig`, runtime)
- `scrapers/parsers/section/constructors/base.py`
- `scrapers/parsers/section/constructors/current.py`
- `scrapers/parsers/section/constructors/former.py`
- `tests/test_scraper_config.py`

### Instancjacje

- `scrapers/scraper_table.py`
- `scrapers/config_table.py`
- `scrapers/parsers/section/table/results/driver.py`
- `scrapers/parsers/section/sponsorship.py`
- `scrapers/parsers/section/grand_prix/by_year.py`
- `scrapers/parsers/seasons/table.py`
- `scrapers/parsers/seasons/cancelled_rounds.py`
- `tests/test_scraper_contract.py`
- `tests/test_table_scraper_options.py`
- `tests/test_table_pipeline.py`
- `tests/test_table_headers.py`
- `tests/test_section_parser_contract.py`
- `tests/test_extractors.py`
- `tests/test_models.py`
- `tests/test_scraper_config.py`

---

## Proponowana kolejność refaktoru (krótko)

1. `DomainRecordService` — najpierw poprawa importów w `scrapers/composition_*.py`, potem testy jednostkowe domen.
2. `InfoboxExtractor` — ujednolicenie kontraktu (`protocol`) i implementacji (`base`), usunięcie starych import paths.
3. `ScraperConfig` — domknięcie kanonicznego modułu `scrapers.base.table.config` + stopniowe wycięcie `scrapers.config_table` i ograniczenie `scrapers.config.ScraperConfig` do runtime.
