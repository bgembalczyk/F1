from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import Sequence

ParserType = Callable[[Any], Any] | str


@dataclass(frozen=True)
class InfoboxSchemaField:
    key: str
    labels: Sequence[str]
    parser: ParserType | None = None
