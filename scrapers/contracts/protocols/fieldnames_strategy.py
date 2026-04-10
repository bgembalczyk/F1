from typing import Protocol

from validation.validator_base import ExportRecord


class FieldnamesStrategyProtocol(Protocol):
    def resolve(
        self,
        data: list[ExportRecord],
        *,
        strategy: str,
    ) -> list[str]: ...
