from collections.abc import Callable

from bs4 import Tag

from models.data.wiki_parser import WikiParserData
from models.payload import WikiParsedPayload
from scrapers.parsers.rules import ParserRule
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.element import ElementParseInput
from scrapers.parsers.wiki.element import ElementRegistry
from scrapers.parsers.wiki.element import WikiElementSet
from scrapers.parsers.wiki.element import build_wikipedia_element_registry
from scrapers.parsers.wiki.element_dispatcher import ElementDispatcher


class WikiElementParsingMixin:
    def __init__(
        self,
        *,
        element_parsers: WikiElementSet | None = None,
        element_registry: ElementRegistry | None = None,
    ) -> None:
        resolved_parsers = element_parsers
        if resolved_parsers is None:
            msg = "element_parsers must be provided by composition root"
            raise ValueError(msg)
        self.infobox_parser = resolved_parsers.infobox_parser
        self.list_parser = resolved_parsers.list_parser
        self.table_parser = resolved_parsers.table_parser
        self.navbox_parser = resolved_parsers.navbox_parser
        self.references_parser = resolved_parsers.references_parser
        self._paragraph_parser = resolved_parsers.paragraph_parser
        self._figure_parser = resolved_parsers.figure_parser
        resolved_registry = element_registry or build_wikipedia_element_registry(
            parsers=WikiElementSet(
                infobox_parser=self.infobox_parser,
                paragraph_parser=self._paragraph_parser,
                figure_parser=self._figure_parser,
                list_parser=self.list_parser,
                table_parser=self.table_parser,
                navbox_parser=self.navbox_parser,
                references_parser=self.references_parser,
            ),
        )
        self.element_registry = resolved_registry
        self.dispatcher = ElementDispatcher(registry=resolved_registry)
        self._parser_rules: list[ParserRule] = []

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

        parse_input = ElementParseInput(
            tag=el,
            metadata=section_context.html_metadata,
            section_context=section_context,
        )
        return self.dispatcher.dispatch(
            parse_input=parse_input,
            section_context=section_context,
        )

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
            "type": rule.result_type,
        }
