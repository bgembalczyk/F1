from typing import TypedDict

from models.types import WikiParserData


class WikiParsedPayload(TypedDict):
    """Wspólny payload zwracany przez parsery elementów wiki."""

    kind: str
    source_section_id: str | None
    confidence: float
    raw_html_fragment: str
    data: WikiParserData
    # legacy compatibility:
    type: str
