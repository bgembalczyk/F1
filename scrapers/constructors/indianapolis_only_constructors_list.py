from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.list.indianapolis_only_scraper import IndianapolisOnlyListScraper
from scrapers.base.source_catalog import CONSTRUCTORS_LIST
from scrapers.wiki.parsers.elements.list import ListParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class IndianapolisOnlyListParser(ListParser):
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


class IndianapolisOnlySubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._list_parser = IndianapolisOnlyListParser()

    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> dict[str, Any]:
        list_root = element.find(["ul", "ol"])
        if isinstance(list_root, Tag):
            return self._list_parser.parse(list_root)
        return self.parse_group(list(element.children), *args, **kwargs)

    def parse_group(
        self,
        elements: list,
        *_args: Any,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        for candidate in elements:
            if isinstance(candidate, Tag) and candidate.name in {"ul", "ol"}:
                return self._list_parser.parse(candidate)
        return {"items": []}


class IndianapolisOnlyConstructorsListScraper(IndianapolisOnlyListScraper):
    url = CONSTRUCTORS_LIST.base_url
    record_key = "constructor"
    url_key = "constructor_url"
    domain_name = "constructors"
    record_type = "constructor"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._sub_section_parser = IndianapolisOnlySubSectionParser()

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        root_list = self._find_list_root(soup)
        parsed = self._sub_section_parser.parse(root_list)
        records = parsed.get("items", [])
        for record in records:
            constructor = record.get("chassis_constructor")
            if not isinstance(constructor, dict):
                continue
            if not self.include_urls:
                constructor.pop("url", None)
                continue
            url = constructor.get("url")
            if isinstance(url, str):
                constructor["url"] = self._full_url(url)
        return records
