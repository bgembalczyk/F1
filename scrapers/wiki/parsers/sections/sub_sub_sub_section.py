from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from scrapers.wiki.parsers.sections.contants import TOP_SECTION_NAME

if TYPE_CHECKING:
    from collections.abc import Callable

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.base import WikiParser
from scrapers.wiki.parsers.elements.figure import FigureParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser
from scrapers.wiki.parsers.elements.list_parser import ListParser
from scrapers.wiki.parsers.elements.navbox import NavBoxParser
from scrapers.wiki.parsers.elements.paragraph import ParagraphParser
from scrapers.wiki.parsers.elements.references_wrap import ReferencesWrapParser
from scrapers.wiki.parsers.elements.table import TableParser
from scrapers.wiki.parsers.section_adapter import SectionExtractionContext


def _split_into_parts(
    children: list[Tag],
    heading_class: str,
) -> list[tuple[str, str | None, list[Tag]]]:
    """Dzieli listę elementów na części według nagłówków danego poziomu."""
    parts: list[tuple[str, str | None, list[Tag]]] = []
    current_name: str = TOP_SECTION_NAME
    current_anchor: str | None = None
    current_elements: list[Tag] = []

    for child in children:
        if not isinstance(child, Tag):
            continue
        classes = child.get("class") or []
        if heading_class in classes:
            parts.append((current_name, current_anchor, current_elements))
            heading_tag = child.find(name=True, recursive=False)
            current_anchor = heading_tag.get("id") if heading_tag else None
            current_name = (
                heading_tag.get_text(" ", strip=True)
                if heading_tag
                else TOP_SECTION_NAME
            )
            current_elements = []
        else:
            current_elements.append(child)

    parts.append((current_name, current_anchor, current_elements))
    return parts


class WikiElementParserMixin:
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
        self.register_parser_rule(
            predicate=lambda el: el.name == "p",
            parser=self.paragraph_parser.parse,
            result_type="paragraph",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "figure",
            parser=self.figure_parser.parse,
            result_type="figure",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "ul",
            parser=self.list_parser.parse,
            result_type="list",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "table"
            and "infobox" in self._get_classes(el),
            parser=self.infobox_parser.parse,
            result_type="infobox",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "table"
            and "wikitable" in self._get_classes(el),
            parser=self.table_parser.parse,
            result_type="table",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "div"
            and el.get("role") == "navigation"
            and "navbox" in self._get_classes(el),
            parser=self.navbox_parser.parse,
            result_type="navbox",
        )
        self.register_parser_rule(
            predicate=lambda el: el.name == "div"
            and any("references-wrap" in c for c in self._get_classes(el)),
            parser=self.references_wrap_parser.parse,
            result_type="references_wrap",
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
                return {
                    "kind": rule.result_type,
                    "source_section_id": section_context.section_id,
                    "confidence": 1.0,
                    "raw_html_fragment": str(el),
                    "data": rule.parser(el),
                    # legacy compatibility:
                    "type": rule.result_type,
                }

        if el.name in {"div", "span"}:
            nested = [
                child
                for child in el.find_all(recursive=False)
                if isinstance(child, Tag)
            ]
            for nested_el in nested:
                parsed = self._parse_element(nested_el, section_context=section_context)
                if parsed is not None:
                    return parsed
        return None


@dataclass(frozen=True)
class ParserRule:
    predicate: Callable[[Tag], bool]
    parser: Callable[[Tag], Any]
    result_type: str


class SubSubSubSectionParser(WikiElementParserMixin, WikiParser):
    def __init__(self) -> None:
        WikiElementParserMixin.__init__(self)

    def parse(
        self,
        element: Tag,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        return self.parse_group(list(element.children), context=context)

    def parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> dict[str, Any]:
        section_context = context or SectionExtractionContext()
        tags = [c for c in elements if isinstance(c, Tag)]
        return {
            "elements": self.parse_elements(tags, section_context=section_context),
        }
