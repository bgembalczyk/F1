from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GrandPrixByYearRecordInput:
    """Input contract for by-year grand prix mapper.

    Input:
    - record: dict parsed from table row
    Output:
    - normalized record dict or None for "not held" rows.
    """

    record: dict[str, Any]
