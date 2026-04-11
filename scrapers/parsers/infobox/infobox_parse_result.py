from typing import Any
from typing import TypeAlias

from scrapers.parsers.parse_result import ParseResult

InfoboxPayload: TypeAlias = dict[str, Any]
InfoboxParseResult: TypeAlias = ParseResult[InfoboxPayload]

__all__ = ["InfoboxParseResult", "InfoboxPayload"]
