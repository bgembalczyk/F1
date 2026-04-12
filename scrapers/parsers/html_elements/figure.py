from bs4 import Tag

from models.data.parsed.html_elements import FigureElementData
from scrapers.parsers.contracts.wiki_figure_parser_abc import WikiFigureParserABC
from scrapers.parsers.text_cleaning import extract_text


class FigureElementParser(WikiFigureParserABC):
    def parse(self, raw: Tag) -> FigureElementData:
        caption_tag = raw.find("figcaption")
        img_tag = raw.find("img")
        src = img_tag.get("src") if img_tag else None
        return {
            "caption": extract_text(caption_tag),
            "src": src if isinstance(src, str) else None,
        }
