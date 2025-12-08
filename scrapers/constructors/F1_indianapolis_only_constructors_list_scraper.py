from typing import Dict, Any, Optional

from bs4 import Tag

from scrapers.base.list.scrapper import F1ListScraper
from scrapers.base.run import run_and_export


class F1IndianapolisOnlyConstructorsListScraper(F1ListScraper):
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
    run_and_export(
        F1IndianapolisOnlyConstructorsListScraper,
        "../../data/wiki/constructors/f1_indianapolis_only_constructors.json",
        "../../data/wiki/constructors/f1_indianapolis_only_constructors.csv",
        include_urls=True,
    )
