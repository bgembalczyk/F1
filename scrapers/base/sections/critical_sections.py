from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriticalSection:
    section_id: str
    alternative_section_ids: tuple[str, ...] = ()
