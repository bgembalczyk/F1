from typing import Dict, Any, Optional

from bs4 import Tag

from scrapers.base.list.scrapper import F1ListScraper


class F1IndianapolisOnlyEngineManufacturersListScraper(F1ListScraper):
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
    from main import main

    main()
