from typing import Any
from typing import TypeVar

WikiRecord = dict[str, Any]
WikiRecords = list[WikiRecord]

TWikiInput = TypeVar("TWikiInput")
TWikiOutput = TypeVar("TWikiOutput")


__all__ = [
    "TWikiInput",
    "TWikiOutput",
    "WikiRecord",
    "WikiRecords",
]
