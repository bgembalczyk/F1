from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol
from typing import TypeVar

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
