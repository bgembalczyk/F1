# Module naming migration map (old -> new)

Migracja dla domen kluczowych: `drivers`, `constructors`, `circuits`, `seasons`, `grands_prix`.

## List scrapers

- `scrapers.list_scraper_drivers.F1DriversListScraper` -> `scrapers.drivers_list_scraper.DriversListScraper`
- `scrapers.constructors_list.ConstructorsListScraper` -> `scrapers.constructors_list_scraper.ConstructorsListScraper`
- `scrapers.circuits_list_scraper.CircuitsListScraper` -> `scrapers.circuits_list_scraper.CircuitsListScraper`
- `scrapers.list_scraper_seasons.SeasonsListScraper` -> `scrapers.seasons_list_scraper.SeasonsListScraper`
- `scrapers.list_scraper_grands_prix.GrandsPrixListScraper` -> `scrapers.grands_prix_list_scraper.GrandsPrixListScraper`

## Detail scrapers

- `scrapers.single_scraper_drivers.SingleDriverScraper` -> `scrapers.drivers_detail_scraper.DriversDetailScraper`
- `scrapers.constructors_single_scraper.SingleConstructorScraper` -> `scrapers.constructors_detail_scraper.ConstructorsDetailScraper`
- `scrapers.circuits_single_scraper.F1SingleCircuitScraper` -> `scrapers.circuits_detail_scraper.CircuitsDetailScraper`
- `scrapers.single_scraper_seasons.SingleSeasonScraper` -> `scrapers.seasons_detail_scraper.SeasonsDetailScraper`
- `scrapers.single_scraper_grands_prix.F1SingleGrandPrixScraper` -> `scrapers.grands_prix_detail_scraper.GrandsPrixDetailScraper`

## Pipeline services

- `scrapers.services.domain_record.driver_pipeline_service.DriverPipelineService` -> `scrapers.drivers_pipeline_service.DriversPipelineService`
- `scrapers.services.domain_record.constructor_pipeline_service.ConstructorPipelineService` -> `scrapers.constructors_pipeline_service.ConstructorsPipelineService`
- `scrapers.services.domain_record.circuit_pipeline_service.CircuitPipelineService` -> `scrapers.circuits_pipeline_service.CircuitsPipelineService`
- `scrapers.services.domain_record.season_pipeline_service.SeasonPipelineService` -> `scrapers.seasons_pipeline_service.SeasonsPipelineService`
- *(new canonical shell)* -> `scrapers.grands_prix_pipeline_service.GrandsPrixPipelineService`

## Factories

- `scrapers.composition_drivers.DriverScraperCompositionFactory` -> `scrapers.drivers_factory.DriversFactory`
- `scrapers.constructors_composition.ConstructorScraperCompositionFactory` -> `scrapers.constructors_factory.ConstructorsFactory`
- `scrapers.circuits_composition.CircuitScraperCompositionFactory` -> `scrapers.circuits_factory.CircuitsFactory`
- `scrapers.composition_seasons.SeasonScraperCompositionFactory` -> `scrapers.seasons_factory.SeasonsFactory`
- *(new canonical factory)* -> `scrapers.grands_prix_factory.GrandsPrixFactory`
