from __future__ import annotations

from typing import Any
from typing import Protocol


class Fetcher(Protocol):
    """Infrastructure layer: fetches raw source payload (HTTP/file/cache)."""

    def fetch(self, source: str) -> Any: ...


class Parser(Protocol):
    """Adapter layer: parses raw payload into structured technical DTOs."""

    def parse(self, raw_payload: Any) -> Any: ...


class Normalizer(Protocol):
    """Application layer: normalizes parsed values into canonical representations."""

    def normalize(self, parsed_payload: Any) -> Any: ...


class Assembler(Protocol):
    """Domain layer: composes normalized parts into domain records."""

    def assemble(self, payload: Any) -> dict[str, Any] | None: ...


class Exporter(Protocol):
    """Output layer: serializes assembled records to a destination format."""

    def export(self, records: list[dict[str, Any]]) -> None: ...
