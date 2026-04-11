# Module naming migration map

## Status

Migracja nazewnictwa modułów została zakończona. Aliasowe moduły (`*_compat`, `*_alias`, `*_shim`, deprecated wrappers) zostały wycofane z warstw domenowych.

## Canonical modules in use

### List scrapers

- `scrapers.list_scraper_drivers.F1DriversListScraper`
- `scrapers.constructors_list.ConstructorsListScraper`
- `scrapers.circuits_list_scraper.CircuitsListScraper`
- `scrapers.list_scraper_seasons.SeasonsListScraper`
- `scrapers.list_scraper_grands_prix.GrandsPrixListScraper`

### Detail scrapers

- `scrapers.single_scraper_drivers.SingleDriverScraper`
- `scrapers.constructors_single_scraper.SingleConstructorScraper`
- `scrapers.circuits_single_scraper.F1SingleCircuitScraper`
- `scrapers.single_scraper_seasons.SingleSeasonScraper`
- `scrapers.single_scraper_grands_prix.F1SingleGrandPrixScraper`

### Pipeline services

- `scrapers.composition_drivers.DriverScraperCompositionFactory` -> `scrapers.drivers_factory.DriversFactory`
- `scrapers.constructors_composition.ConstructorScraperCompositionFactory` -> `scrapers.constructors_factory.ConstructorsFactory`
- `scrapers.circuits_composition.CircuitScraperCompositionFactory` -> `scrapers.circuits_factory.CircuitsFactory`
- `scrapers.composition_seasons.SeasonScraperCompositionFactory` -> `scrapers.seasons_factory.SeasonsFactory`
- *(new canonical factory)* -> `scrapers.grands_prix_factory.GrandsPrixFactory`


## Infobox extraction (role families)

### Canonical modules

- `scrapers.infobox.extraction.base`
- `scrapers.infobox.extraction.protocol`
- `scrapers.infobox.extraction.factory`
- `scrapers.infobox.extraction.registry`
- `scrapers.infobox.extraction.service`
- `scrapers.infobox.extraction.mixins`

### Extractors (`*_extractor.py`)

- `scrapers.infobox.extraction.extractor.base` -> `scrapers.infobox.extraction.extractor.base_extractor`
- `scrapers.infobox.extraction.extractor.circuit` -> `scrapers.infobox.extraction.extractor.circuit_extractor`

### Orchestrators (`*_orchestrator.py`)

- `scrapers.infobox.extraction.service.base` -> `scrapers.infobox.extraction.service.base_orchestrator`
- `scrapers.infobox.extraction.service.strategy` -> `scrapers.infobox.extraction.service.strategy_orchestrator`
- `scrapers.infobox.extraction.service.driver` -> `scrapers.infobox.extraction.service.driver_orchestrator`
- `scrapers.infobox.extraction.service.constructor` -> `scrapers.infobox.extraction.service.constructor_orchestrator`
- `scrapers.infobox.extraction.service.circuit` -> `scrapers.infobox.extraction.service.circuit_orchestrator`

### Status migracji

Migracja importów jest zakończona; nowe i utrzymywane call-site'y używają wyłącznie nazw kanonicznych z mapy powyżej.
