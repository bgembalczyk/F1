from __future__ import annotations

from dataclasses import dataclass
from typing import Generic
from typing import TypeVar

from scrapers.base.types import JsonValue

ParsePayloadT = TypeVar("ParsePayloadT")


@dataclass(frozen=True)
class ParseMetadata:
    parser: str
    source: str
    extras: dict[str, JsonValue]


@dataclass(frozen=True)
class ParseResult(Generic[ParsePayloadT]):
    payload: ParsePayloadT
    metadata: ParseMetadata


__all__ = ["ParseMetadata", "ParseResult", "ParsePayloadT"]
