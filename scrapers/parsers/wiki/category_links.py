from bs4 import Tag

from models.category.group import CategoryGroup
from models.data.parsed.category_links import CategoryLinksParsedData
from scrapers.extractors.category_links_extractor import CategoryLinksExtractor
from scrapers.parsers.parser_abc import ParserABC


class CategoryLinksParser(ParserABC[Tag, CategoryLinksParsedData]):
    """Parser linków do kategorii Wikipedii (wyłącznie transformacja danych)."""

    def __init__(self, *, extractor: CategoryLinksExtractor | None = None) -> None:
        self.extractor = extractor or CategoryLinksExtractor()

    def parse(self, element: Tag) -> CategoryLinksParsedData:
        extracted_groups = self.extractor.extract(element)
        categories: list[CategoryGroup] = [
            {
                "category": group.category,
                "links": [
                    {
                        "text": link.text,
                        "href": link.href,
                    }
                    for link in group.links
                ],
            }
            for group in extracted_groups
        ]
        return {"categories": categories}
