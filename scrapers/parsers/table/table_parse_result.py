from typing import Any
from typing import TypeAlias

from scrapers.parsers.parse_result import ParseResult

TablePayload: TypeAlias = dict[str, Any]
TableParseResult: TypeAlias = ParseResult[TablePayload]

__all__ = ["TableParseResult", "TablePayload"]
