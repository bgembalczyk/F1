from bs4 import Tag

from models.data.parsed.html_elements import ParagraphElementData
from scrapers.parsers.parser_abc import ParserABC
from scrapers.text_cleaning import extract_text


class ParagraphElementParser(ParserABC[Tag, ParagraphElementData]):
    def parse(self, raw: Tag) -> ParagraphElementData:
        return {"text": extract_text(raw) or ""}
