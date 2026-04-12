from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

InT = TypeVar("InT")
OutT = TypeVar("OutT")
RecordT_co = TypeVar("RecordT_co", covariant=True)
RowInputT_contra = TypeVar("RowInputT_contra", contravariant=True)
TableInputT_contra = TypeVar("TableInputT_contra", contravariant=True)


SoupOut = TypeVar("SoupOut")
TagOut = TypeVar("TagOut")


BundleT_co = TypeVar("BundleT_co", bound="ParsingBundle", covariant=True)

In = TypeVar("In")
Out = TypeVar("Out")












__all__ = [
    "InT",
    "OutT",
    "RecordT_co",
    "RowInputT_contra",
    "TableInputT_contra",
]
