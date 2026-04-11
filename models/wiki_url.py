from __future__ import annotations

from typing_extensions import Self


class WikiUrl(str):
    __slots__ = ()

    def __new__(cls, value: str) -> Self:
        cleaned = " ".join(str(value).strip().split())
        if not cleaned:
            msg = "WikiUrl cannot be empty."
            raise ValueError(msg)
        return str.__new__(cls, cleaned)

    @classmethod
    def from_raw(cls, value: str | WikiUrl) -> WikiUrl:
        return value if isinstance(value, cls) else cls(value)

    def to_export(self) -> str:
        return str(self)
