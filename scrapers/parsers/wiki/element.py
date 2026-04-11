from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.infobox.html import WikiInfoboxHtmlParser
from scrapers.parsers.rules import ParserRule
from scrapers.parsers.wiki.list import ListParser
from scrapers.parsers.table.wiki.table import WikiTableHtmlParser
from scrapers.parsers.wiki.figure import FigureParser
from scrapers.parsers.wiki.navbox import NavBoxParser
from scrapers.parsers.wiki.paragraph import ParagraphParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


@dataclass(frozen=True)
class WikiElementParsers:
    infobox_parser: WikiInfoboxHtmlParser
    paragraph_parser: ParagraphParser
    figure_parser: FigureParser
    list_parser: ListParser
    table_parser: WikiTableHtmlParser
    navbox_parser: NavBoxParser
    references_wrap_parser: ReferencesWrapParser


@dataclass(frozen=True)
class ElementParserRegistry:
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
    parsers: WikiElementParsers,
    section_parser: Callable[[Tag], WikiParserData] | None = None,
) -> ElementParserRegistry:
    section_rules: tuple[ParserRule, ...] = ()
    if section_parser is not None:
        # h2/h3/h4 + kontener - parsery sekcji/podsekcji
        section_rules = (
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and any(
                        heading in ElementParserRegistry._get_classes(el)
                        for heading in ("mw-heading2", "mw-heading3", "mw-heading4")
                    )
                ),
                parser=section_parser,
                result_type="section",
            ),
        )
    return ElementParserRegistry(
        rules=(
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
            ParserRule(
                predicate=lambda el: (
                    el.name == "table"
                    and "infobox" in ElementParserRegistry._get_classes(el)
                ),
                parser=parsers.infobox_parser.parse,
                result_type="infobox",
            ),
            *section_rules,
            ParserRule(
                predicate=lambda el: el.name == "figure",
                parser=parsers.figure_parser.parse,
                result_type="figure",
            ),
            ParserRule(
                predicate=lambda el: el.name == "p",
                parser=parsers.paragraph_parser.parse,
                result_type="paragraph",
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
                    and "reflist" in ElementParserRegistry._get_classes(el)
                ),
                parser=parsers.references_wrap_parser.parse,
                result_type="references_wrap",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and any(
                        "references-wrap" in c
                        for c in ElementParserRegistry._get_classes(el)
                    )
                ),
                parser=parsers.references_wrap_parser.parse,
                result_type="references_wrap",
            ),
        ),
    )


def build_default_wiki_element_parsers() -> WikiElementParsers:
    return WikiElementParsers(
        infobox_parser=WikiInfoboxHtmlParser(),
        paragraph_parser=ParagraphParser(),
        figure_parser=FigureParser(),
        list_parser=ListParser(),
        table_parser=WikiTableHtmlParser(),
        navbox_parser=NavBoxParser(),
        references_wrap_parser=ReferencesWrapParser(),
    )


def build_default_wikipedia_element_registry() -> ElementParserRegistry:
    return build_wikipedia_element_registry(parsers=build_default_wiki_element_parsers())
