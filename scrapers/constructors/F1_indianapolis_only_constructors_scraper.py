from typing import Dict, Any, Optional

from bs4 import Tag

from scrapers.F1_list_scrapper import F1ListScraper


class F1IndianapolisOnlyConstructorsScraper(F1ListScraper):
    """
    Lista konstruktorów 'Indianapolis 500 only'
    ze strony List_of_Formula_One_constructors.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_constructors"
    section_id = "Indianapolis_500_only"

    def parse_item(self, li: Tag) -> Optional[Dict[str, Any]]:
        a = li.find("a")
        name = li.get_text(" ", strip=True)
        if not name:
            return None

        record: Dict[str, Any] = {"constructor": name}
        if self.include_urls and a and a.has_attr("href"):
            record["constructor_url"] = self._full_url(a["href"])
        return record


if __name__ == "__main__":
    scraper = F1IndianapolisOnlyConstructorsScraper(include_urls=True)

    indy_only = scraper.fetch()
    print(f"Pobrano rekordów: {len(indy_only)}")

    scraper.to_json("f1_indianapolis_only_constructors.json")
    scraper.to_csv("f1_indianapolis_only_constructors.csv")

    # opcjonalnie:
    # import pprint
    # pprint.pp(indy_only[:5])
    # df = scraper.to_dataframe()
    # print(df.head())
