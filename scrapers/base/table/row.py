from dataclasses import dataclass
from typing import Sequence

from bs4 import Tag


@dataclass(frozen=True)
class TableRow:
    headers: Sequence[str]
    cells: Sequence[Tag]
    raw_tr: Tag
