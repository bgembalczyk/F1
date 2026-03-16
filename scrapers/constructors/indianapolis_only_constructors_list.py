from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper
from scrapers.base.run_config import RunConfig


class IndianapolisOnlyConstructorsListScraper(IndianapolisOnlyListScraper):
    """
    Lista konstruktorów 'Indianapolis 500 only'
    ze strony List_of_Formula_One_constructors.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    record_key = "constructor"
    url_key = "constructor_url"


if __name__ == "__main__":
    run_and_export(
        IndianapolisOnlyConstructorsListScraper,
        "constructors/f1_indianapolis_only_constructors.json",
        "constructors/f1_indianapolis_only_constructors.csv",
        run_config=RunConfig(
            output_category="constructors",
            output_layer="raw",
            legacy_output_enabled=True,
            parser_version="1.0.0",
            schema_version="1.0.0",
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
