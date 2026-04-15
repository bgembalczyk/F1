from bs4 import Tag

from models.data.parsed.html_elements import NavboxElementData
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.wiki.wiki_element_parser_abc import WikiElementType
from scrapers.text_cleaning import extract_text


class NavboxElementParser(ParserABC[Tag, NavboxElementData]):
    element_type: WikiElementType = "navbox"

    def parse(self, raw: Tag) -> NavboxElementData:
        title_tag = raw.find(class_="navbox-title")
        links: list[dict[str, str | None]] = []
        for anchor in raw.find_all("a"):
            href = anchor.get("href")
            if isinstance(href, str):
                links.append({"text": extract_text(anchor), "href": href})
        return {"title": extract_text(title_tag), "links": links}
