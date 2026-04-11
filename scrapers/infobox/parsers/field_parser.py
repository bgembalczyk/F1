from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic
from typing import Protocol
from typing import TypeVar
from typing import runtime_checkable

Input = TypeVar("Input")
Output = TypeVar("Output")


@runtime_checkable
class InfoboxFieldParser(Protocol, Generic[Input, Output]):
    def parse(self, value: Input) -> Output: ...


@dataclass(frozen=True)
class CallableInfoboxFieldParser(Generic[Input, Output]):
    _parser: Callable[[Input], Output]

    def parse(self, value: Input) -> Output:
        return self._parser(value)


__all__ = [
    "InfoboxFieldParser",
    "CallableInfoboxFieldParser",
]
