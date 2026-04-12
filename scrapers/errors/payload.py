from typing import TypedDict


class ScraperErrorPayload(TypedDict):
    """Typed payload for exporting scraper exceptions to pipeline logs."""

    code: str
    level: str
    code_id: str
    code_description: str
    message: str
    domain: str
    source: str | None
    record: str | None
    suggestion: str | None
    source_name: str | None
    cause: str | None
    category: str
    behavior: str
    critical: bool
    url: str | None
    section_id: str | None
    parser_name: str | None
    run_id: str | None
