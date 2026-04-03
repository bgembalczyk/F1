from __future__ import annotations

from typing import Protocol
from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

T = TypeVar("T")


class ProgressAdapter(Protocol):
    def wrap(
        self,
        iterable: Iterable[T],
        *,
        desc: str,
        unit: str,
    ) -> Iterable[T]: ...


class TqdmProgressAdapter:
    def wrap(
        self,
        iterable: Iterable[T],
        *,
        desc: str,
        unit: str,
    ) -> Iterable[T]:
        from tqdm import tqdm

        return tqdm(iterable, desc=desc, unit=unit)


class NoOpProgressAdapter:
    def wrap(
        self,
        iterable: Iterable[T],
        *,
        _desc: str,
        _unit: str,
    ) -> Iterable[T]:
        return iterable
