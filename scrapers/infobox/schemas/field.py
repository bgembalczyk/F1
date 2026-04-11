from collections.abc import Callable
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

ParserType = Callable[[Any], Any] | str


@dataclass(frozen=True)
class InfoboxSchemaField:
    key: str
    labels: Sequence[str]
    parser: ParserType | None = None
