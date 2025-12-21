from pathlib import Path

from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.registry import register_scraper
from scrapers.base.run import RunConfig, run_and_export


@register_scraper(
    "engine_manufacturers_indy",
    "engines/f1_indianapolis_only_engine_manufacturers.json",
    "engines/f1_indianapolis_only_engine_manufacturers.csv",
)
class IndianapolisOnlyEngineManufacturersListScraper(F1ListScraper):
    """
    Lista 'Indianapolis 500 only' dla producentów silników.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers"
    section_id = "Indianapolis_500_only"

    record_key = "manufacturer"
    url_key = "manufacturer_url"


if __name__ == "__main__":
    run_and_export(
        IndianapolisOnlyEngineManufacturersListScraper,
        "engines/f1_indianapolis_only_engine_manufacturers.json",
        "engines/f1_indianapolis_only_engine_manufacturers.csv",
        run_config=RunConfig(output_dir=Path("../../data/wiki")),
    )
