from __future__ import annotations

from abc import ABC
from typing import Any


class HasTableParserABC(ABC):
    _table_parser: Any


__all__ = ["HasTableParserABC"]
