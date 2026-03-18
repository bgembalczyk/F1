from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper


class IndianapolisOnlyConstructorsListScraper(IndianapolisOnlyListScraper):
    """
    Lista konstruktorów 'Indianapolis 500 only'
    ze strony List_of_Formula_One_constructors.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    record_key = "constructor"
    url_key = "constructor_url"


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
