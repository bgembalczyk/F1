from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from bs4 import Tag

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class ParserRule:
    predicate: Callable[[Tag], bool]
    parser: Callable[[Tag], Any]
    result_type: str
