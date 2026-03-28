from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from bs4 import Tag


@dataclass(frozen=True)
class ParserRule:
    predicate: Callable[[Tag], bool]
    parser: Callable[[Tag], Any]
    result_type: str
