from __future__ import annotations

import re

from typing_extensions import Self


class SectionId(str):
    __slots__ = ()

    def __new__(cls, value: str) -> Self:
        text = str(value).strip()
        if not text:
            msg = "SectionId cannot be empty."
            raise ValueError(msg)
        cleaned = re.sub(r"\s+", "_", text.lower())
        return str.__new__(cls, cleaned)

    @classmethod
    def from_raw(cls, value: str | SectionId) -> SectionId:
        return value if isinstance(value, cls) else cls(value)

    def to_export(self) -> str:
        return str(self)
