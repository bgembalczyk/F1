from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from scrapers.parsers.html_elements.base import BaseHtmlElementParser
from scrapers.parsers.text_cleaning import extract_text


class ParagraphElementParser(BaseHtmlElementParser[ParagraphElementData]):
    def parse(self, raw: Tag) -> ParagraphElementData:
        return {"text": extract_text(raw) or ""}
