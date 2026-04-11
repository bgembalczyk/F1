from typing import Any

from bs4 import Tag

from scrapers.parsers.wiki.list import ListParser


class IndianapolisConstructorsListParser(ListParser):
    def parse(self, element: Tag) -> dict[str, list[dict[str, Any]]]:
        items: list[dict[str, Any]] = []
        for li in element.find_all("li", recursive=False):
            anchor = li.find("a")
            constructor = li.get_text(" ", strip=True)
            if not constructor:
                continue
            row: dict[str, Any] = {
                "chassis_constructor": {
                    "text": constructor,
                },
            }
            if anchor and anchor.has_attr("href"):
                row["chassis_constructor"]["url"] = anchor["href"]
            items.append(row)
        return {"items": items}
