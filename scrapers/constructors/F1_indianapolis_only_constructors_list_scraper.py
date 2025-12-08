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
    scraper = F1IndianapolisOnlyConstructorsListScraper(include_urls=True)

    indy_only = scraper.fetch()
    print(f"Pobrano rekordów: {len(indy_only)}")

    scraper.to_json(
        "../../data/wiki/constructors/f1_indianapolis_only_constructors.json"
    )
    scraper.to_csv("../../data/wiki/constructors/f1_indianapolis_only_constructors.csv")

    # opcjonalnie:
    # import pprint
    # pprint.pp(indy_only[:5])
    # df = scraper.to_dataframe()
    # print(df.head())
