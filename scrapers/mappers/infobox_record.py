from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InfoboxRecordInput:
    """Input contract for infobox -> record mapper.

    Input: mapping-like infobox payload.
    Output: plain dict[str, Any] ready for export.
    """

    payload: Mapping[str, Any]


class InfoboxRecordMapper:
    """Maps infobox payloads to normalized record dictionaries.

    Normalization rules:
    - input must be mapping,
    - string keys are stripped,
    - values are preserved except recursive normalization of nested
      dict/list containers into plain Python structures.
    """

    def map(self, payload: InfoboxRecordInput | Mapping[str, Any]) -> dict[str, Any]:
        source = payload.payload if isinstance(payload, InfoboxRecordInput) else payload
        if not isinstance(source, Mapping):
            msg = "Infobox mapper contract violation: payload must be mapping."
            raise TypeError(msg)
        return {
            self._normalize_key(key): self._normalize_value(value)
            for key, value in source.items()
        }

    def map_many(self, payloads: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [self.map(payload) for payload in payloads]

    def _normalize_key(self, key: Any) -> str:
        return str(key).strip()

    def _normalize_value(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                self._normalize_key(nested_key): self._normalize_value(nested_value)
                for nested_key, nested_value in value.items()
            }
        if isinstance(value, list):
            return [self._normalize_value(item) for item in value]
        return value
