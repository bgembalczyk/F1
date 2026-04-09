from __future__ import annotations


from typing import Any
from typing import Self


class EntityName(str):
    __slots__ = ()

    def __new__(cls, value: Any) -> Self:
        text = " ".join(str(value).strip().split())
        if not text:
            msg = "EntityName cannot be empty."
            raise ValueError(msg)
        return str.__new__(cls, text)

    @classmethod
    def from_raw(cls, value: str | EntityName) -> EntityName:
        return value if isinstance(value, cls) else cls(value)

    def to_export(self) -> str:
        return str(self)
