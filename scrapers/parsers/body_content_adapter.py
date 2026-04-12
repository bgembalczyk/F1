from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.parsers.wiki.extractors.body_content_parts import BodyContentParts


class BodyContentAdapter:
    """Adapter wyszukujący sekcje DOM potrzebne do złożenia body content."""

    def adapt(self, element: Tag) -> BodyContentParts:
        return BodyContentParts(
            catlinks=self.find_catlinks(element),
            content_text=self.find_content_text(element),
        )

    @staticmethod
    def find_body_content(soup: BeautifulSoup) -> Tag | None:
        return soup.find("div", id="bodyContent")

    @staticmethod
    def find_catlinks(element: Tag) -> Tag | None:
        catlinks = element.find("div", id="catlinks")
        return catlinks if isinstance(catlinks, Tag) else None

    @staticmethod
    def find_content_text(element: Tag) -> Tag | None:
        content_text = element.find(
            "div",
            id=lambda value: value and "content-text" in value,
            class_=lambda value: (
                value
                and "body-content" in (value if isinstance(value, list) else value.split())
            ),
        )
        if content_text is None:
            content_text = element.find(
                "div",
                class_=lambda value: (
                    value
                    and "mw-content-ltr" in (value if isinstance(value, list) else value.split())
                ),
            )
        return content_text if isinstance(content_text, Tag) else None


__all__ = ["BodyContentParts", "BodyContentAdapter"]
