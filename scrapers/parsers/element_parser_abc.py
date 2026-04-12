from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import Literal

from bs4 import Tag

from scrapers.parsers.constants_contracts import TagOut
from scrapers.parsers.tag_parser_abc import HtmlTagParserABC

ElementType = Literal[
    "table",
    "list",
    "section",
    "infobox",
    "navbox",
    "references",
    "paragraph",
    "figure",
]


class HtmlElementParserABC(HtmlTagParserABC[TagOut], ABC, Generic[TagOut]):
    """Canonical HTML-element parsing layer.

    Sits between the root ParserABC[In, Out] and the specialized Wiki ABCs:

        ParserABC[In, Out]
          └── HtmlTagParserABC[TagOut]
                └── HtmlElementParserABC[TagOut]   ← this layer
                      ├── WikiTableParserABC
                      ├── WikiListParserABC
                      ├── WikiSectionParserABC
                      ├── WikiInfoboxParserABC
                      ├── WikiNavboxParserABC
                      └── WikiFigureParserABC
    """

    element_type: ElementType

    @abstractmethod
    def parse(self, raw: Tag) -> TagOut: ...



class ListElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "list"


class TableElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "table"


class InfoboxElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "infobox"


class SectionElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "section"


class NavboxElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "navbox"


class ReferencesElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "references"


class ParagraphElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "paragraph"


class FigureElementParserABC(HtmlElementParserABC[TagOut], ABC, Generic[TagOut]):
    element_type: ElementType = "figure"
