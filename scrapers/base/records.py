from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, TypeAlias

RawRecord: TypeAlias = Dict[str, Any]
NormalizedRecord: TypeAlias = Dict[str, Any]
ExportRecord: TypeAlias = Dict[str, Any]


@dataclass(frozen=True)
class RawRecords:
    data: List[RawRecord]


@dataclass(frozen=True)
class NormalizedRecords:
    data: List[NormalizedRecord]


@dataclass(frozen=True)
class ExportRecords:
    data: List[ExportRecord]
