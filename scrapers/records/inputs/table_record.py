from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TableRecordInput:
    """Input contract for table row -> record mapper.

    Input: mapping-like row payload.
    Output: plain dict[str, Any].
    """

    payload: Mapping[str, Any]


