from __future__ import annotations

import re
from typing import Any

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


class SeasonYear(int):
    _MIN_YEAR = 1900
    _MAX_YEAR = 3000

    def __new__(cls, value: int | str | SeasonYear) -> Self:
        year = int(value)
        if year < cls._MIN_YEAR or year > cls._MAX_YEAR:
            msg = (
                f"SeasonYear out of supported range: {year}. "
                f"Expected {cls._MIN_YEAR}-{cls._MAX_YEAR}."
            )
            raise ValueError(msg)
        return int.__new__(cls, year)

    @classmethod
    def from_raw(cls, value: int | str | SeasonYear | None) -> SeasonYear | None:
        if value is None:
            return None
        return value if isinstance(value, cls) else cls(value)

    def to_export(self) -> int:
        return int(self)


class SectionId(str):
    __slots__ = ()

    def __new__(cls, value: str) -> Self:
        text = str(value).strip()
        if not text:
            msg = "SectionId cannot be empty."
            raise ValueError(msg)
        cleaned = re.sub(r"\s+", " ", text).strip()
        return str.__new__(cls, cleaned)

    @classmethod
    def from_raw(cls, value: str | SectionId) -> SectionId:
        return value if isinstance(value, cls) else cls(value)

    def to_export(self) -> str:
        return str(self)


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
