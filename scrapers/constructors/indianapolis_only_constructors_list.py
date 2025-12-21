from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.registry import register_scraper
from scrapers.base.run import run_and_export


@register_scraper(
    "constructors_indy",
    "constructors/f1_indianapolis_only_constructors.json",
    "constructors/f1_indianapolis_only_constructors.csv",
)
class IndianapolisOnlyConstructorsListScraper(F1ListScraper):
    """
    Lista konstruktorów 'Indianapolis 500 only'
    ze strony List_of_Formula_One_constructors.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Indianapolis_500_only"

    record_key = "constructor"
    url_key = "constructor_url"


if __name__ == "__main__":
    run_and_export(
        IndianapolisOnlyConstructorsListScraper,
        "../../data/wiki/constructors/f1_indianapolis_only_constructors.json",
        "../../data/wiki/constructors/f1_indianapolis_only_constructors.csv",
    )
