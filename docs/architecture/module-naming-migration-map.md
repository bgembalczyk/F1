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

- `scrapers.drivers_pipeline_service.DriversPipelineService`
- `scrapers.constructors_pipeline_service.ConstructorsPipelineService`
- `scrapers.circuits_pipeline_service.CircuitsPipelineService`
- `scrapers.seasons_pipeline_service.SeasonsPipelineService`
- `scrapers.grands_prix_pipeline_service.GrandsPrixPipelineService`
