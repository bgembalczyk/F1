from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DriverResultsSectionConfig:
    section_id: str
    section_label: str
    header_aliases: tuple[str, ...]


__all__ = [
    "DriverResultsSectionConfig",
]
