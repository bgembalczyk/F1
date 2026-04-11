from __future__ import annotations

from abc import ABC
from typing import Generic
from typing import TypeVar

from scrapers.domain_roles import Parser

Input = TypeVar("Input")
Output = TypeVar("Output")


class InfoboxFieldParser(Parser[Input, Output], ABC, Generic[Input, Output]):
    """Silny kontrakt runtime dla parserów pojedynczych pól infoboxu."""


__all__ = ["InfoboxFieldParser", "Input", "Output"]
