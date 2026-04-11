from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InfoboxRecordInput:
    """Input contract for infobox -> record mapper.

    Input: mapping-like infobox payload.
    Output: plain dict[str, Any] ready for export.
    """

    payload: Mapping[str, Any]
