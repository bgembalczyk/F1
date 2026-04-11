from bs4 import Tag

from models.data.parsed.html_elements import FigureElementData
from scrapers.parsers.html_elements.base import BaseHtmlElementParser
from scrapers.parsers.text_cleaning import extract_text


class FigureElementParser(BaseHtmlElementParser[FigureElementData]):
    def parse(self, element: Tag) -> FigureElementData:
        caption_tag = element.find("figcaption")
        img_tag = element.find("img")
        src = img_tag.get("src") if img_tag else None
        return {
            "caption": extract_text(caption_tag),
            "src": src if isinstance(src, str) else None,
        }
