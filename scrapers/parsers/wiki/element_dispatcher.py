from __future__ import annotations

from dataclasses import dataclass

from models.payload import WikiParsedPayload
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.element_registry import ElementParseInput
from scrapers.parsers.wiki.element_registry import ElementRegistry


@dataclass(frozen=True)
class ElementParserDispatcher:
    """Single dispatcher used by section parsers to delegate element parsing."""

    registry: ElementRegistry

    def dispatch(
        self,
        *,
        parse_input: ElementParseInput,
        section_context: SectionExtractionContext,
    ) -> WikiParsedPayload | None:
        resolved = self.registry.resolve(parse_input)
        if resolved is None:
            return None
        result_type, parser = resolved
        return {
            "kind": result_type,
            "source_section_id": section_context.section_id,
            "confidence": 1.0,
            "raw_html_fragment": str(parse_input.tag),
            "data": parser(parse_input.tag),
            "type": result_type,
        }


__all__ = ["ElementParserDispatcher"]
