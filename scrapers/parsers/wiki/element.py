from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.element_parser_abc import ElementType
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser
from scrapers.parsers.list_element_parser import ListElementParser
from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.rules import ParserRule
from scrapers.parsers.wiki.infobox import WikiInfoboxParser
from scrapers.parsers.wiki.table.html import WikiTableHtmlParser
from scrapers.parsers.wiki.base import WikiListParser
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
    references_wrap_parser: ParserABC[Tag, WikiParserData]
    references_parser: ParserABC[Tag, WikiParserData] | None = None
    section_parser: Callable[[Tag], WikiParserData] | None = None

    def _effective_references_parser(self) -> ParserABC[Tag, WikiParserData]:
        return self.references_parser if self.references_parser is not None else self.references_wrap_parser


@dataclass(frozen=True)
class ElementRegistry:
    rules: tuple[ParserRule, ...]

    @staticmethod
    def _get_classes(el: Tag) -> list[str]:
        classes = el.get("class") or []
        if isinstance(classes, str):
            return classes.split()
        return list(classes)

    def resolve(
        self,
        element: Tag,
    ) -> tuple[str, Callable[[Tag], WikiParserData]] | None:
        for rule in self.rules:
            if rule.predicate(element):
                return rule.result_type, rule.parser
        return None


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

    # Ordered explicit mapping: (element_type, parser_instance).
    # Priority order: infobox before table to handle tables with both classes.
    named_parsers: list[tuple[str, ParserABC]] = [
        ("paragraph", parsers.paragraph_parser),
        ("infobox", parsers.infobox_parser),
        ("table", parsers.table_parser),
        ("list", parsers.list_parser),
        ("figure", parsers.figure_parser),
        ("navbox", parsers.navbox_parser),
        ("references_wrap", parsers._effective_references_parser()),
    ]
    rules: list[ParserRule] = []
    for element_type, parser in named_parsers:
        if element_type not in type_predicates:
            continue
        rules.append(
            ParserRule(
                predicate=type_predicates[element_type],
                parser=parser.parse,
                result_type=element_type,
            ),
        )

    if parsers.section_parser is not None:
        rules.append(
            ParserRule(
                predicate=type_predicates["section"],
                parser=parsers.section_parser,
                result_type="section",
            ),
        )

    return ElementRegistry(
        rules=tuple(rules),
    )


def build_default_wiki_element_parsers() -> WikiElementSet:
    return WikiElementSet(
        infobox_parser=WikiInfoboxHtmlParser(),
        paragraph_parser=WikiParagraphParser(),
        figure_parser=WikiFigureParser(),
        list_parser=ListElementParser(),
        table_parser=WikiTableHtmlParser(),
        navbox_parser=WikiNavboxParser(),
        references_wrap_parser=ReferencesWrapParser(),
        references_parser=ReferencesWrapParser(),
    )


def build_default_wikipedia_element_registry() -> ElementRegistry:
    return build_wikipedia_element_registry(
        parsers=build_default_wiki_element_parsers()
    )

# WikiElementParsers is the canonical public alias for WikiElementSet
WikiElementParsers = WikiElementSet

__all__ = [
    'WikiElementParsers',
    'WikiElementSet',
    'ElementRegistry',
    'build_default_wiki_element_parsers',
    'build_default_wikipedia_element_registry',
    'build_wikipedia_element_registry',
]
