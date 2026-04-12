from __future__ import annotations

from abc import ABC
from typing import Any


class HasTableParserABC(ABC):
    _table_parser: Any


class HasTableMapperABC(ABC):
    _table_mapper: Any


__all__ = ["HasTableMapperABC", "HasTableParserABC"]
