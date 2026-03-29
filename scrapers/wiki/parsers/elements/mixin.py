from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
from scrapers.wiki.parsers.elements.references_wrap import ReferencesWrapParser
from scrapers.wiki.parsers.elements.rules import ParserRule
from scrapers.wiki.parsers.elements.table import TableParser
from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext


class WikiElementParserMixin:
    DEFAULT_PARSER_RULE_SPECS: list[
        tuple[
            Callable[["WikiElementParserMixin", Tag], bool],
            str,
            str,
            int,
        ]
    ] = [
        (lambda mixin, el: el.name == "p", "paragraph_parser", "paragraph", 0),
        (lambda mixin, el: el.name == "figure", "figure_parser", "figure", 1),
        (lambda mixin, el: el.name == "ul", "list_parser", "list", 2),
        (
            lambda mixin, el: el.name == "table" and "infobox" in mixin._get_classes(el),
            "infobox_parser",
            "infobox",
            3,
        ),
        (
            lambda mixin, el: el.name == "table" and "wikitable" in mixin._get_classes(el),
            "table_parser",
            "table",
            4,
        ),
        (
            lambda mixin, el: el.name == "div"
            and el.get("role") == "navigation"
            and "navbox" in mixin._get_classes(el),
            "navbox_parser",
            "navbox",
            5,
        ),
        (
            lambda mixin, el: el.name == "div"
            and any("references-wrap" in c for c in mixin._get_classes(el)),
            "references_wrap_parser",
            "references_wrap",
            6,
        ),
    ]

    def __init__(self) -> None:
        self.infobox_parser = InfoboxParser()
        self.paragraph_parser = ParagraphParser()
        self.figure_parser = FigureParser()
        self.list_parser = ListParser()
        self.table_parser = TableParser()
        self.navbox_parser = NavBoxParser()
        self.references_wrap_parser = ReferencesWrapParser()
        self._parser_rules: list[ParserRule] = []
        self._register_default_parser_rules()

    @staticmethod
    def _get_classes(el: Tag) -> list[str]:
        classes = el.get("class") or []
        if isinstance(classes, str):
            return classes.split()
        return list(classes)

    def register_parser_rule(
        self,
        *,
        predicate: Callable[[Tag], bool],
        parser: Callable[[Tag], Any],
        result_type: str,
        priority: int | None = None,
    ) -> None:
        rule = ParserRule(predicate=predicate, parser=parser, result_type=result_type)
        if priority is None:
            self._parser_rules.append(rule)
            return
        index = max(0, min(priority, len(self._parser_rules)))
        self._parser_rules.insert(index, rule)

    def _register_default_parser_rules(self) -> None:
        for (
            predicate,
            parser_key,
            result_type,
            priority,
        ) in self.DEFAULT_PARSER_RULE_SPECS:
            parser_instance = getattr(self, parser_key)
            self.register_parser_rule(
                predicate=lambda el, rule_predicate=predicate: rule_predicate(self, el),
                parser=parser_instance.parse,
                result_type=result_type,
                priority=priority,
            )

    @staticmethod
    def _has_infobox_class(classes: Any) -> bool:
        if not classes:
            return False
        if isinstance(classes, str):
            classes = classes.split()
        try:
            return "infobox" in list(classes)
        except TypeError:
            return False

    def find_infobox(self, soup: BeautifulSoup) -> Tag | None:
        return soup.find(name="table", class_=self._has_infobox_class)

    def find_infoboxes(self, soup: BeautifulSoup) -> list[Tag]:
        return soup.find_all(name="table", class_=self._has_infobox_class)

    def parse_elements(
        self,
        elements: list[Tag],
        *,
        section_context: SectionExtractionContext,
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for el in elements:
            parsed = self._parse_element(el, section_context=section_context)
            if parsed is not None:
                result.append(parsed)
        return result

    def _parse_element(
        self,
        el: Tag,
        *,
        section_context: SectionExtractionContext,
    ) -> dict[str, Any] | None:
        for rule in self._parser_rules:
            if rule.predicate(el):
                return self._build_parsed_payload(
                    el=el,
                    rule=rule,
                    section_context=section_context,
                )

        if el.name in {"div", "span"}:
            for nested_el in self._iter_direct_child_tags(el):
                parsed = self._parse_element(nested_el, section_context=section_context)
                if parsed is not None:
                    return parsed
        return None

    @staticmethod
    def _iter_direct_child_tags(element: Tag) -> list[Tag]:
        return [
            child
            for child in element.find_all(recursive=False)
            if isinstance(child, Tag)
        ]

    @staticmethod
    def _build_parsed_payload(
        *,
        el: Tag,
        rule: ParserRule,
        section_context: SectionExtractionContext,
    ) -> dict[str, Any]:
        return {
            "kind": rule.result_type,
            "source_section_id": section_context.section_id,
            "confidence": 1.0,
            "raw_html_fragment": str(el),
            "data": rule.parser(el),
            # legacy compatibility:
            "type": rule.result_type,
        }
