from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from validation.validator_base import ExportRecord


class ExporterProtocol(Protocol):
    def to_json(
        self,
        result,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None: ...

    def to_csv(
        self,
        result,
        path: str | Path,
        *,
        fieldnames: Sequence[str] | None = None,
        include_metadata: bool = False,
    ) -> None: ...




