from bs4 import Tag

from models.data.parsed.html_elements import NavboxElementData
from scrapers.parsers.html_elements.base import BaseHtmlElementParser
from scrapers.parsers.text_cleaning import extract_text


class NavboxElementParser(BaseHtmlElementParser[NavboxElementData]):
    def parse(self, element: Tag) -> NavboxElementData:
        title_tag = element.find(class_="navbox-title")
        links: list[dict[str, str | None]] = []
        for anchor in element.find_all("a"):
            href = anchor.get("href")
            if isinstance(href, str):
                links.append({"text": extract_text(anchor), "href": href})
        return {"title": extract_text(title_tag), "links": links}
