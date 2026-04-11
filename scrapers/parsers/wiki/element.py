from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.html_elements.list import ListElementParser
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser
from scrapers.parsers.rules import ParserRule
from scrapers.parsers.table.wiki.table import WikiTableHtmlParser
from scrapers.parsers.wiki.base import WikiListParser
from scrapers.parsers.wiki.figure import WikiFigureParser
from scrapers.parsers.wiki.infobox import WikiInfoboxParser
from scrapers.parsers.wiki.navbox import WikiNavboxParser
from scrapers.parsers.wiki.paragraph import WikiParagraphParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser
from scrapers.parsers.wiki.table import WikiTableParser


@dataclass(frozen=True)
class WikiElementSet:
    infobox_parser: WikiInfoboxParser
    paragraph_parser: WikiParagraphParser
    figure_parser: WikiFigureParser
    list_parser: WikiListParser
    table_parser: WikiTableParser
    navbox_parser: WikiNavboxParser
    references_wrap_parser: ReferencesWrapParser


@dataclass(frozen=True)
class ElementRegistry:
    """Registry parserów elementów Wikipedii.

    Rejestr dobiera parser po typie elementu (tag + klasy CSS), bez logiki domenowej.
    """

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
    section_parser: Callable[[Tag], WikiParserData] | None = None,
) -> ElementRegistry:
    section_rules: tuple[ParserRule, ...] = ()
    if parsers.section_parser is not None:
        section_rules = (
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and any(
                        heading in ElementRegistry._get_classes(el)
                        for heading in ("mw-heading2", "mw-heading3", "mw-heading4")
                    )
                ),
                parser=parsers.section_parser,
                result_type="section",
            ),
        )
    return ElementRegistry(
        rules=(
            ParserRule(
                predicate=lambda el: (
                    el.name == "table"
                    and "wikitable" in ElementRegistry._get_classes(el)
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
                predicate=lambda el: (
                    el.name == "table"
                    and "infobox" in ElementRegistry._get_classes(el)
                ),
                parser=parsers.infobox_parser.parse,
                result_type="infobox",
            ),
            ParserRule(
                predicate=lambda el: el.name == "figure",
                parser=parsers.figure_parser.parse,
                result_type="figure",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and "navbox" in ElementRegistry._get_classes(el)
                ),
                parser=parsers.navbox_parser.parse,
                result_type="navbox",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and "reflist" in ElementRegistry._get_classes(el)
                ),
                parser=parsers.references_wrap_parser.parse,
                result_type="references_wrap",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and any(
                        "references-wrap" in c
                        for c in ElementRegistry._get_classes(el)
                    )
                ),
                parser=parsers.references_parser.parse,
                result_type="references",
            ),
        ),
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
    )


def build_default_wikipedia_element_registry() -> ElementRegistry:
    return build_wikipedia_element_registry(
        parsers=build_default_wiki_element_parsers()
    )


# Backward-compatible aliases.
WikiElementParsers = WikiElementSet
ElementParserRegistry = ElementRegistry
