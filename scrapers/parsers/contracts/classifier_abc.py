from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

InT = TypeVar("InT")
OutT = TypeVar("OutT")


class ClassifierABC(ABC, Generic[InT, OutT]):
    """Canonical classifier contract for non-parser classification stages."""

    @abstractmethod
    def classify(self, raw: InT) -> OutT | None: ...


__all__ = ["ClassifierABC", "InT", "OutT"]
