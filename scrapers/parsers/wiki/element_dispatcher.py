from __future__ import annotations

from dataclasses import dataclass

from models.payload import WikiParsedPayload
from scrapers.parsers.section.extraction_context import SectionExtractionContext
from scrapers.parsers.wiki.element_payload_factory import ElementParseResult
from scrapers.parsers.wiki.element_payload_factory import ElementPayloadFactory
from scrapers.parsers.wiki.element_payload_factory import PassthroughElementClassifier
from scrapers.parsers.wiki.element_payload_factory import WikiParsedPayloadMapper
from scrapers.parsers.wiki.element_registry import ElementParseInput
from scrapers.parsers.wiki.element_registry import ElementRegistry


@dataclass(frozen=True)
class ElementParserDispatcher:
    """Single dispatcher used by section parsers to delegate element parsing."""

    registry: ElementRegistry
    payload_factory: ElementPayloadFactory = ElementPayloadFactory(
        classifier=PassthroughElementClassifier(),
        mapper=WikiParsedPayloadMapper(),
    )

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
        parse_result = ElementParseResult(
            element_type=result_type,
            payload=parser(parse_input.tag),
            raw_html_fragment=str(parse_input.tag),
            section_id=section_context.section_id,
            confidence=1.0,
        )
        return self.payload_factory.create(parse_result)


__all__ = ["ElementParserDispatcher"]
