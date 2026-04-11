from bs4 import Tag

from scrapers.parsers.html_elements.list import ListElementParser


class IndianapolisOnlyListParser(ListElementParser):
    def parse(self, element: Tag) -> dict[str, list[dict[str, str]]]:
        items: list[dict[str, str]] = []
        for li in element.find_all("li", recursive=False):
            anchor = li.find("a")
            engine_constructor = li.get_text(" ", strip=True)
            if not engine_constructor:
                continue
            row: dict[str, str] = {"engine_constructor": engine_constructor}
            if anchor and anchor.has_attr("href"):
                row["engine_constructor_url"] = anchor["href"]
            items.append(row)
        return {"items": items}
