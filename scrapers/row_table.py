from collections.abc import Sequence
from dataclasses import dataclass

from bs4 import Tag


@dataclass(frozen=True)
class TableRow:
    headers: Sequence[str]
    cells: Sequence[Tag]
    raw_tr: Tag
    header_cells: Sequence[Tag] | None = None
