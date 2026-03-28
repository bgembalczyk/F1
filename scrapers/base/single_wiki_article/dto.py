from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(frozen=True)
class InfoboxPayloadDTO:
    data: Any = field(default_factory=list)


@dataclass(frozen=True)
class TablesPayloadDTO:
    data: Any = field(default_factory=list)


@dataclass(frozen=True)
class SectionsPayloadDTO:
    data: Any = field(default_factory=list)
