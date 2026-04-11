from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Generic
from typing import TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")


class BaseInfoboxFieldParser(ABC, Generic[Input, Output]):
    """Common abstract base for infobox field parsers."""

    @abstractmethod
    def parse(self, value: Input) -> Output:
        """Parse raw infobox value into a structured output payload."""


__all__ = ["BaseInfoboxFieldParser"]
