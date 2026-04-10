from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from bs4 import BeautifulSoup



@dataclass(frozen=True)
class DriverResultsSectionConfig:
    section_id: str
    section_label: str
    header_aliases: tuple[str, ...]




__all__ = [
    "DriverResultsSectionConfig",
]
