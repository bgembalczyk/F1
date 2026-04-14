from __future__ import annotations

from dataclasses import dataclass

from models.data.wiki_parser import WikiParserData
from models.payload import WikiParsedPayload


@dataclass(frozen=True)
class ElementParseResult:
    """Output of HTML element parser stage (Tag -> payload data)."""

    element_type: str
    payload: WikiParserData
    raw_html_fragment: str
    section_id: str | None
    confidence: float = 1.0


@dataclass(frozen=True)
class ElementPayloadFactory:
    """Strict parser pipeline: parse result -> payload."""

    def create(self, parse_result: ElementParseResult) -> WikiParsedPayload:
        return {
            "kind": parse_result.element_type,
            "source_section_id": parse_result.section_id,
            "confidence": parse_result.confidence,
            "raw_html_fragment": parse_result.raw_html_fragment,
            "data": parse_result.payload,
            "type": parse_result.element_type,
        }


__all__ = [
    "ElementParseResult",
    "ElementPayloadFactory",
]
