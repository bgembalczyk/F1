from bs4 import Tag

from models.data.parsed.html_elements import NavboxElementData
from scrapers.parsers.contracts.wiki_elements import WikiNavboxElementParserABC
from scrapers.text_cleaning import extract_text


class NavboxElementParser(WikiNavboxElementParserABC):
    def parse(self, raw: Tag) -> NavboxElementData:
        title_tag = raw.find(class_="navbox-title")
        links: list[dict[str, str | None]] = []
        for anchor in raw.find_all("a"):
            href = anchor.get("href")
            if isinstance(href, str):
                links.append({"text": extract_text(anchor), "href": href})
        return {"title": extract_text(title_tag), "links": links}
