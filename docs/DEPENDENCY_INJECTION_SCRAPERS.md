# Podmiana zależności w `Single*Scraper` i `Complete*DataExtractor`

Po refaktoryzacji kluczowe scrapery przyjmują podmienne zależności przez argumenty konstruktora (`*_service`, `assembler`, `*_factory`).

## Co można podmienić

- `SingleDriverScraper`: `infobox_service`, `sections_service_factory`, `assembler`.
- `SingleConstructorScraper`: `infobox_service`, `sections_service_factory`, `assembler`, `article_tables_parser`.
- `SingleSeasonScraper`: `text_sections_service_factory`, fabryki parserów sekcji (`*_section_parser_factory`), `assembler`.
- `SingleEngineManufacturerScraper`: `infobox_parser_factory`, `article_tables_parser`.
- `Complete*DataExtractor`: fabryki `list_scraper_factory`, `single_scraper_factory` (oraz warianty list scraperów dla konstruktorów/silników).

## Przykład (test integracyjny)

```python
from scrapers.drivers.single_scraper import SingleDriverScraper

class FakeAssembler:
    def assemble(self, **kwargs):
        return {"fake": True, "payload": kwargs}

scraper = SingleDriverScraper(
    assembler=FakeAssembler(),
)
```

## Przykład (extension)

```python
from scrapers.seasons.complete_scraper import CompleteSeasonDataExtractor
from scrapers.seasons.single_scraper import SingleSeasonScraper

class CustomSingleSeasonScraper(SingleSeasonScraper):
    ...

extractor = CompleteSeasonDataExtractor(
    single_scraper_factory=CustomSingleSeasonScraper,
)
```

To podejście upraszcza testowanie, A/B porównania parserów i rozszerzanie pipeline'u bez forka bazowych klas.
