from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from scrapers.parsers.html_elements.list import ListElementParser
from scrapers.parsers.infobox.wiki_html import WikiInfoboxHtmlParser
from scrapers.parsers.rules import ParserRule
from scrapers.parsers.table.table.table import WikiTableHtmlParser
from scrapers.parsers.wiki.figure import WikiFigureParser
from scrapers.parsers.wiki.navbox import WikiNavboxParser
from scrapers.parsers.wiki.paragraph import WikiParagraphParser
from scrapers.parsers.wiki.references_wrap import ReferencesWrapParser


@dataclass(frozen=True)
class WikiElementSet:
    table_parser: WikiTableHtmlParser
    list_parser: ListElementParser
    infobox_parser: WikiInfoboxHtmlParser
    section_parser: Callable[[Tag], WikiParserData] | None = None


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
    paragraph_parser = WikiParagraphParser()
    figure_parser = WikiFigureParser()
    navbox_parser = WikiNavboxParser()
    references_parser = ReferencesWrapParser()

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
                predicate=lambda el: el.name == "p",
                parser=paragraph_parser.parse,
                result_type="paragraph",
            ),
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
                parser=figure_parser.parse,
                result_type="figure",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "div" and "navbox" in ElementRegistry._get_classes(el)
                ),
                parser=navbox_parser.parse,
                result_type="navbox",
            ),
            ParserRule(
                predicate=lambda el: (
                    el.name == "div"
                    and (
                        "reflist" in ElementRegistry._get_classes(el)
                        or any(
                            "references-wrap" in c
                            for c in ElementRegistry._get_classes(el)
                        )
                    )
                ),
                parser=references_parser.parse,
                result_type="references",
            ),
        ),
    )


def build_default_wiki_element_parsers() -> WikiElementSet:
    return WikiElementSet(
        infobox_parser=WikiInfoboxHtmlParser(),
        list_parser=ListElementParser(),
        table_parser=WikiTableHtmlParser(),
    )


def build_default_wikipedia_element_registry() -> ElementRegistry:
    return build_wikipedia_element_registry(parsers=build_default_wiki_element_parsers())
