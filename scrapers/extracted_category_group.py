from dataclasses import dataclass

from scrapers.extracted_category_link import ExtractedCategoryLink


@dataclass(frozen=True)
class ExtractedCategoryGroup:
    category: str | None
    links: list[ExtractedCategoryLink]
