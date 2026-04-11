from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.rules import ParserRule
from scrapers.parsers.wiki.element_figure import WikiFigureElementParser
from scrapers.parsers.wiki.element_infobox import WikiInfoboxElementParser
from scrapers.parsers.wiki.element_list import WikiListElementParser
from scrapers.parsers.wiki.element_navbox import WikiNavboxElementParser
from scrapers.parsers.wiki.element_paragraph import WikiParagraphElementParser
from scrapers.parsers.wiki.element_references import WikiReferencesElementParser
from scrapers.parsers.wiki.element_table import WikiTableElementParser


@dataclass(frozen=True)
class WikiElementParsers:
    table_parser: WikiTableElementParser
    list_parser: WikiListElementParser
    section_parser: Callable[[Tag], WikiParserData] | None
    infobox_parser: WikiInfoboxElementParser
    paragraph_parser: WikiParagraphElementParser
    figure_parser: WikiFigureElementParser
    navbox_parser: WikiNavboxElementParser
    references_parser: WikiReferencesElementParser


@dataclass(frozen=True)
class ElementParserRegistry:
    """Registry parserów elementów Wikipedii bez logiki domenowej."""

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
    parsers: WikiElementParsers,
) -> ElementParserRegistry:
    section_rules: tuple[ParserRule, ...] = ()
    if parsers.section_parser is not None:
        section_rules = (
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and any(
                        heading in ElementParserRegistry._get_classes(el)
                        for heading in ("mw-heading2", "mw-heading3", "mw-heading4")
                    )
                ),
                parser=parsers.section_parser,
                result_type="section",
            ),
        )

    return ElementParserRegistry(
        rules=(
            ParserRule(
                predicate=lambda el: (
                    el.name == "table"
                    and "infobox" in ElementParserRegistry._get_classes(el)
                ),
                parser=parsers.infobox_parser.parse,
                result_type="infobox",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "table"
                    and "wikitable" in ElementParserRegistry._get_classes(el)
                ),
                parser=parsers.table_parser.parse,
                result_type="table",
            ),
            ParserRule(
                predicate=lambda el: el.name in {"ul", "ol"},
                parser=parsers.list_parser.parse,
                result_type="list",
            ),
            *section_rules,
            ParserRule(
                predicate=lambda el: el.name == "p",
                parser=parsers.paragraph_parser.parse,
                result_type="paragraph",
            ),
            ParserRule(
                predicate=lambda el: el.name == "figure",
                parser=parsers.figure_parser.parse,
                result_type="figure",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and "navbox" in ElementParserRegistry._get_classes(el)
                ),
                parser=parsers.navbox_parser.parse,
                result_type="navbox",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and (
                        "reflist" in ElementParserRegistry._get_classes(el)
                        or any(
                            "references-wrap" in c
                            for c in ElementParserRegistry._get_classes(el)
                        )
                    )
                ),
                parser=parsers.references_parser.parse,
                result_type="references",
            ),
        ),
    )
