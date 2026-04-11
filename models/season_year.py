from __future__ import annotations

from typing_extensions import Self


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
