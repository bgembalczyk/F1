from typing import Dict, Any, Optional

from bs4 import Tag

from scrapers.F1_list_scrapper import F1ListScraper


class F1IndianapolisOnlyEngineManufacturersScraper(F1ListScraper):
    """
    Lista 'Indianapolis 500 only' dla producentów silników.
    """

    url = "https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers"
    section_id = "Indianapolis_500_only"

    def parse_item(self, li: Tag) -> Optional[Dict[str, Any]]:
        a = li.find("a")
        name = li.get_text(" ", strip=True)
        if not name:
            return None
        record: Dict[str, Any] = {"manufacturer": name}
        if self.include_urls and a and a.has_attr("href"):
            record["manufacturer_url"] = self._full_url(a["href"])
        return record


if __name__ == "__main__":
    scraper = F1IndianapolisOnlyEngineManufacturersScraper(include_urls=True)

    indy_engines = scraper.fetch()
    print(f"Pobrano rekordów: {len(indy_engines)}")

    scraper.to_json("f1_indianapolis_only_engine_manufacturers.json")
    scraper.to_csv("f1_indianapolis_only_engine_manufacturers.csv")

    # opcjonalnie:
    # for e in indy_engines:
    #     print(e)
    # df = scraper.to_dataframe()
    # print(df.head())
