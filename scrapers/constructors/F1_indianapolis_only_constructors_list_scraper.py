from scrapers.base.list.scrapper import F1ListScraper


class F1IndianapolisOnlyConstructorsListScraper(F1ListScraper):
    """
    Lista konstruktorów 'Indianapolis 500 only'
    ze strony List_of_Formula_One_constructors.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Indianapolis_500_only"

    record_key = "constructor"
    url_key = "constructor_url"


if __name__ == "__main__":
    from main import main

    main()
