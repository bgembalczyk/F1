from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias

from bs4 import Tag

from scrapers.parsers.parser_abc import ParserABC
from scrapers.parsers.rules import ParserRule
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.section.toolbox import SectionParserToolbox
from scrapers.parsers.section.toolbox import build_default_section_toolbox
from scrapers.parsers.wiki.element import ElementParseInput
from scrapers.parsers.wiki.element import ElementRegistry
from scrapers.parsers.wiki.element_dispatcher import ElementDispatcher
from scrapers.parsers.wiki.element_payload_factory import ElementParseResult

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Iterable

    from models.data.wiki_parser import WikiParserData
    from models.payload import WikiParsedPayload


SectionLevelParseResult: TypeAlias = dict[str, Any]


class RecursiveSectionParser(ParserABC):
    """Generic recursive parser for heading levels h2-h6.

    Supports a leaf mode when ``heading_class`` is ``None``: instead of
    splitting elements by heading, it returns all child elements directly as
    ``{"elements": [...]}``.
    """

    heading_class: str | None = "mw-heading3"
    output_key: str = "sub_sections"

    def __init__(
        self,
        *,
        heading_class: str | None = None,
        output_key: str | None = None,
        child_parser: RecursiveSectionParser | None = None,
        toolbox: SectionParserToolbox | None = None,
    ) -> None:
        if heading_class is not None:
            self.heading_class = heading_class
        if output_key is not None:
            self.output_key = output_key
        self.child_parser = child_parser
        self.toolbox = toolbox or build_default_section_toolbox()
        resolved_parsers = self.toolbox.element_parsers
        self.infobox_parser = resolved_parsers.infobox_parser
        self.list_parser = resolved_parsers.list_parser
        self.table_parser = resolved_parsers.table_parser
        self.navbox_parser = resolved_parsers.navbox_parser
        self.references_parser = resolved_parsers.references_parser
        self._paragraph_parser = resolved_parsers.paragraph_parser
        self._figure_parser = resolved_parsers.figure_parser
        resolved_registry = self.toolbox.element_registry
        self.element_registry: ElementRegistry = resolved_registry
        self.dispatcher = ElementDispatcher(registry=resolved_registry)
        self._parser_rules: list[ParserRule] = []

    @property
    def element_parsers(self):
        return self.toolbox.element_parsers

    @staticmethod
    def filter_child_tags(elements: Iterable[object]) -> list[Tag]:
        return [element for element in elements if isinstance(element, Tag)]

    def parse(
        self,
        element: Tag | list[Tag],
        *,
        context: SectionExtractionContext | None = None,
    ) -> SectionLevelParseResult:
        elements = list(element.children) if isinstance(element, Tag) else element
        return self._parse_group(elements, context=context)

    def parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> SectionLevelParseResult:
        return self._parse_group(elements, context=context)

    def _parse_group(
        self,
        elements: list,
        *,
        context: SectionExtractionContext | None = None,
    ) -> SectionLevelParseResult:
        section_context = context or SectionExtractionContext()
        tags = self.filter_child_tags(elements)

        if self.heading_class is None:
            return {
                "elements": self.parse_elements(tags, section_context=section_context),
            }

        parts = self.toolbox.section_locator.locate(
            tags,
            heading_class=self.heading_class,
        )
        sections: list[dict[str, Any]] = []

        for part in parts:
            section_id = self.toolbox.section_assembler.assemble(
                section_name=part.section_label,
                heading_anchor=part.heading_anchor,
                context=section_context,
                fragment={},
            )["section_id"]
            child_context = section_context.with_section(
                section_name=part.section_label,
                section_id=section_id,
            )
            fragment = self._parse_children(part.elements, context=child_context)
            sections.append(
                self.toolbox.section_assembler.assemble(
                    section_name=part.section_label,
                    heading_anchor=part.heading_anchor,
                    context=section_context,
                    fragment=fragment,
                ),
            )

        return {self.output_key: sections}

    def _parse_children(
        self,
        elements: list[Tag],
        *,
        context: SectionExtractionContext,
    ) -> SectionLevelParseResult:
        if self.child_parser is not None:
            return self.child_parser.parse(elements, context=context)
        return {
            "elements": self.parse_elements(
                elements,
                section_context=context,
            ),
        }

    # ---------- Element parsing (previously WikiElementParsingMixin) ----------

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

    def _build_parsed_payload(
        self,
        *,
        el: Tag,
        rule: ParserRule,
        section_context: SectionExtractionContext,
    ) -> WikiParsedPayload:
        parse_result = ElementParseResult(
            element_type=rule.result_type,
            payload=rule.parser(el),
            raw_html_fragment=str(el),
            section_id=section_context.section_id,
            confidence=1.0,
        )
        payload = self.dispatcher.payload_factory.create(parse_result)
        if payload is None:
            return {
                "kind": rule.result_type,
                "source_section_id": section_context.section_id,
                "confidence": 1.0,
                "raw_html_fragment": str(el),
                "data": rule.parser(el),
                "type": rule.result_type,
            }
        return payload

    def apply_table_mapper(self, payload: dict[str, Any]) -> None:
        """Recursively applies the table mapper to nested dictionaries."""
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self.apply_table_mapper(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self.apply_table_mapper(item)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        """Applies the table parser to a list of elements."""
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            mapper = getattr(self, "_table_mapper", None)
            if mapper is None:
                mapper = getattr(self, "_table_parser", None)
            if mapper is None:
                continue
            if hasattr(mapper, "map"):
                parsed = mapper.map(data)
            else:
                parsed = mapper.parse(data)
            if parsed is not None:
                element["data"] = parsed

    def _apply_table_parser_to_sections(self, payload: dict[str, Any], key: str) -> None:
        """Applies table parser to elements in sections recursively."""
        for section in payload.get(key, []):
            if isinstance(section, dict):
                self._apply_for_elements(section.get("elements", []))
                self._apply_table_parser_to_sections(section, key)


__all__ = ["RecursiveSectionParser", "SectionLevelParseResult"]
