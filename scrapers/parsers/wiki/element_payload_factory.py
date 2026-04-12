from __future__ import annotations

from dataclasses import dataclass

from models.data.wiki_parser import WikiParserData
from models.payload import WikiParsedPayload
from scrapers.parsers.contracts.mapping import WikiElementClassifierABC
from scrapers.parsers.contracts.mapping import WikiElementPayloadMapperABC


@dataclass(frozen=True)
class ElementParseResult:
    """Output of HTML element parser stage (Tag -> payload data)."""

    element_type: str
    payload: WikiParserData
    raw_html_fragment: str
    section_id: str | None
    confidence: float = 1.0


class PassthroughElementClassifier(WikiElementClassifierABC[ElementParseResult, str]):
    """Default classifier: emit element_type as classification label."""

    def classify(self, raw: ElementParseResult) -> str | None:
        return raw.element_type


class WikiParsedPayloadMapper(
    WikiElementPayloadMapperABC[ElementParseResult, str],
):
    """Mapper/factory stage creating canonical WikiParsedPayload records."""

    def map(
        self,
        raw: ElementParseResult,
        *,
        element_type: str,
        section_id: str | None,
        classification: str,
        raw_html_fragment: str,
        confidence: float,
    ) -> WikiParsedPayload:
        _ = classification
        return {
            "kind": element_type,
            "source_section_id": section_id,
            "confidence": confidence,
            "raw_html_fragment": raw_html_fragment,
            "data": raw.payload,
            "type": element_type,
        }


@dataclass(frozen=True)
class ElementPayloadFactory:
    """Strict parser pipeline: parse result -> optional classify -> payload mapper."""

    classifier: WikiElementClassifierABC[ElementParseResult, str]
    mapper: WikiElementPayloadMapperABC[ElementParseResult, str]

    def create(self, parse_result: ElementParseResult) -> WikiParsedPayload | None:
        classification = self.classifier.classify(parse_result)
        if classification is None:
            return None
        return self.mapper.map(
            parse_result,
            element_type=parse_result.element_type,
            section_id=parse_result.section_id,
            classification=classification,
            raw_html_fragment=parse_result.raw_html_fragment,
            confidence=parse_result.confidence,
        )


__all__ = [
    "ElementParseResult",
    "ElementPayloadFactory",
    "PassthroughElementClassifier",
    "WikiParsedPayloadMapper",
]
