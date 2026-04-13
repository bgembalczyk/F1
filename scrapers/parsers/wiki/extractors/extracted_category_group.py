from dataclasses import dataclass

from scrapers.parsers.wiki.extractors.extracted_category_link import (
    ExtractedCategoryLink,
)


@dataclass(frozen=True)
class ExtractedCategoryGroup:
    category: str | None
    links: list[ExtractedCategoryLink]
