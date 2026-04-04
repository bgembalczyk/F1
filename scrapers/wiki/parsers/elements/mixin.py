from collections.abc import Callable

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.wiki.parsers.elements.parsers import WikiElementParsers
from scrapers.wiki.parsers.elements.rules import ParserRule
from scrapers.wiki.parsers.sections.data_classes import SectionExtractionContext
from scrapers.wiki.parsers.types import WikiParsedPayload
from scrapers.wiki.parsers.types import WikiParserData


class WikiElementParserMixin:
    def __init__(
        self,
        *,
        element_parsers: WikiElementParsers | None = None,
    ) -> None:
        resolved_parsers = element_parsers
        if resolved_parsers is None:
            msg = "element_parsers must be provided by composition root"
            raise ValueError(msg)
        self.infobox_parser = resolved_parsers.infobox_parser
        self.paragraph_parser = resolved_parsers.paragraph_parser
        self.figure_parser = resolved_parsers.figure_parser
        self.list_parser = resolved_parsers.list_parser
        self.table_parser = resolved_parsers.table_parser
        self.navbox_parser = resolved_parsers.navbox_parser
        self.references_wrap_parser = resolved_parsers.references_wrap_parser
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
        parser: Callable[[Tag], WikiParserData],
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
            predicate=lambda el: (
                el.name == "table" and "infobox" in self._get_classes(el)
            ),
            parser=self.infobox_parser.parse,
            result_type="infobox",
        )
        self.register_parser_rule(
            predicate=lambda el: (
                el.name == "table" and "wikitable" in self._get_classes(el)
            ),
            parser=self.table_parser.parse,
            result_type="table",
        )
        self.register_parser_rule(
            predicate=lambda el: (
                el.name == "div"
                and el.get("role") == "navigation"
                and "navbox" in self._get_classes(el)
            ),
            parser=self.navbox_parser.parse,
            result_type="navbox",
        )
        self.register_parser_rule(
            predicate=lambda el: (
                el.name == "div"
                and any("references-wrap" in c for c in self._get_classes(el))
            ),
            parser=self.references_wrap_parser.parse,
            result_type="references_wrap",
        )

    @staticmethod
    def _has_infobox_class(classes: object) -> bool:
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
    ) -> list[WikiParsedPayload]:
        result: list[WikiParsedPayload] = []
        for el in elements:
            result.extend(
                self._parse_element_list(el, section_context=section_context),
            )
        return result

    def _parse_element_list(
        self,
        el: Tag,
        *,
        section_context: SectionExtractionContext,
    ) -> list[WikiParsedPayload]:
        parsed = self._parse_element(el, section_context=section_context)
        if parsed is not None:
            classes = self._get_classes(el)
            if (
                parsed.get("kind") == "paragraph"
                and isinstance(parsed.get("data"), dict)
                and (
                    not str(parsed["data"].get("text", "")).strip()
                    or "mw-empty-elt" in classes
                )
            ):
                nested_results = self._parse_nested_elements(
                    el,
                    section_context=section_context,
                )
                if nested_results:
                    return nested_results
            return [parsed]

        return self._parse_nested_elements(el, section_context=section_context)

    def _parse_nested_elements(
        self,
        el: Tag,
        *,
        section_context: SectionExtractionContext,
    ) -> list[WikiParsedPayload]:
        nested_results: list[WikiParsedPayload] = []
        for nested_el in self._iter_direct_child_tags(el):
            nested_results.extend(
                self._parse_element_list(
                    nested_el,
                    section_context=section_context,
                ),
            )
        return nested_results

    def _parse_element(
        self,
        el: Tag,
        *,
        section_context: SectionExtractionContext,
    ) -> WikiParsedPayload | None:
        for rule in self._parser_rules:
            if rule.predicate(el):
                return self._build_parsed_payload(
                    el=el,
                    rule=rule,
                    section_context=section_context,
                )
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
    ) -> WikiParsedPayload:
        return {
            "kind": rule.result_type,
            "source_section_id": section_context.section_id,
            "confidence": 1.0,
            "raw_html_fragment": str(el),
            "data": rule.parser(el),
            # legacy compatibility:
            "type": rule.result_type,
        }
