from __future__ import annotations

from dataclasses import dataclass

from bs4 import Tag


@dataclass(frozen=True)
class ExtractedCategoryLink:
    text: str
    href: str


@dataclass(frozen=True)
class ExtractedCategoryGroup:
    category: str | None
    links: list[ExtractedCategoryLink]


class CategoryLinksExtractor:
    """Ekstrahuje surowe grupy linków kategorii z bloku `catlinks`."""

    def extract(self, element: Tag) -> list[ExtractedCategoryGroup]:
        groups: list[ExtractedCategoryGroup] = []

        for catlinks_div in element.find_all("div", id=True):
            category = self._extract_category_name(catlinks_div)
            links = self._extract_links(catlinks_div, skip_first=True)
            if links:
                groups.append(ExtractedCategoryGroup(category=category, links=links))

        if groups:
            return groups

        fallback_links = self._extract_links(element)
        return [ExtractedCategoryGroup(category=None, links=fallback_links)]

    @staticmethod
    def _extract_category_name(container: Tag) -> str | None:
        category_anchor = container.find("a")
        if not isinstance(category_anchor, Tag):
            return None
        return category_anchor.get_text(" ", strip=True) or None

    @staticmethod
    def _extract_links(container: Tag, *, skip_first: bool = False) -> list[ExtractedCategoryLink]:
        anchors = container.find_all("a")
        if skip_first:
            anchors = anchors[1:]

        links: list[ExtractedCategoryLink] = []
        for anchor in anchors:
            href = anchor.get("href")
            if not isinstance(href, str):
                continue
            links.append(
                ExtractedCategoryLink(
                    text=anchor.get_text(" ", strip=True),
                    href=href,
                ),
            )
        return links


__all__ = [
    "ExtractedCategoryLink",
    "ExtractedCategoryGroup",
    "CategoryLinksExtractor",
]
