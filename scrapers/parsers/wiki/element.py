from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.element_parser_abc import ElementType
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser
from scrapers.parsers.list_element_parser import ListElementParser
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.wiki.element_registry import ElementParseInput
from scrapers.parsers.wiki.element_registry import ElementParserRegistration
from scrapers.parsers.wiki.element_registry import ElementRegistry
from scrapers.parsers.wiki.table.html import WikiTableHtmlParser
from scrapers.parsers.wiki.figure import WikiFigureParser
from scrapers.parsers.wiki.navbox import WikiNavboxParser
from scrapers.parsers.wiki.paragraph import WikiParagraphParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


@dataclass(frozen=True)
class WikiElementSet:
    infobox_parser: ParserABC[Tag, WikiParserData]
    paragraph_parser: ParserABC[Tag, WikiParserData]
    figure_parser: ParserABC[Tag, WikiParserData]
    list_parser: ParserABC[Tag, WikiParserData]
    table_parser: ParserABC[Tag, WikiParserData]
    navbox_parser: ParserABC[Tag, WikiParserData]
    references_parser: ParserABC[Tag, WikiParserData]
    section_parser: Callable[[Tag], WikiParserData] | None = None


def build_wikipedia_element_registry(
    *,
    parsers: WikiElementSet,
) -> ElementRegistry:
    type_predicates: dict[ElementType, Callable[[Tag], bool]] = {
        "paragraph": lambda el: el.name == "p",
        "infobox": lambda el: (
            el.name == "table"
            and "infobox" in ElementRegistry._get_classes(el)
        ),
        "table": lambda el: (
            el.name == "table"
            and "wikitable" in ElementRegistry._get_classes(el)
        ),
        "list": lambda el: el.name in {"ul", "ol"},
        "section": lambda el: (
            el.name == "div"
            and any(
                heading in ElementRegistry._get_classes(el)
                for heading in ("mw-heading2", "mw-heading3", "mw-heading4")
            )
        ),
        "figure": lambda el: el.name == "figure",
        "navbox": lambda el: (
            el.name == "div" and "navbox" in ElementRegistry._get_classes(el)
        ),
        "references_wrap": lambda el: (
            el.name == "div"
            and (
                "reflist" in ElementRegistry._get_classes(el)
                or any("references-wrap" in c for c in ElementRegistry._get_classes(el))
            )
        ),
    }

    named_parsers: list[tuple[ElementType, ParserABC[Tag, WikiParserData]]] = [
        ("paragraph", parsers.paragraph_parser),
        ("infobox", parsers.infobox_parser),
        ("table", parsers.table_parser),
        ("list", parsers.list_parser),
        ("figure", parsers.figure_parser),
        ("navbox", parsers.navbox_parser),
        ("references_wrap", parsers.references_parser),
    ]

    registrations = tuple(
        ElementParserRegistration(
            element_type=element_type,
            parser=parser.parse,
            parser_class=type(parser),
        )
        for element_type, parser in named_parsers
    )

    return ElementRegistry(
        registrations=registrations,
        type_predicates=type_predicates,
    )


def build_default_wiki_element_parsers() -> WikiElementSet:
    return WikiElementSet(
        infobox_parser=WikiInfoboxHtmlParser(),
        paragraph_parser=WikiParagraphParser(),
        figure_parser=WikiFigureParser(),
        list_parser=ListElementParser(),
        table_parser=WikiTableHtmlParser(),
        navbox_parser=WikiNavboxParser(),
        references_parser=ReferencesWrapParser(),
    )


def build_default_wikipedia_element_registry() -> ElementRegistry:
    return build_wikipedia_element_registry(
        parsers=build_default_wiki_element_parsers()
    )


# WikiElementParsers is the canonical public alias for WikiElementSet
WikiElementParsers = WikiElementSet

__all__ = [
    "ElementParseInput",
    "ElementParserRegistration",
    'WikiElementParsers',
    'WikiElementSet',
    'ElementRegistry',
    'build_default_wiki_element_parsers',
    'build_default_wikipedia_element_registry',
    'build_wikipedia_element_registry',
]
