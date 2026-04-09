from __future__ import annotations

from enum import Enum
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import overload

from models.records.builders import RECORD_BUILDERS
from models.records.type import RecordType

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping







def normalize_record_type(record_type: RecordType | str) -> RecordType | str:
    if isinstance(record_type, RecordType):
        return record_type
    return RECORD_TYPE_ALIASES.get(record_type, record_type)




@overload
def build_record(record_type: RecordType, record: Mapping[str, Any]) -> Any: ...


@overload
def build_record(record_type: str, record: Mapping[str, Any]) -> Any: ...


def build_record(record_type: RecordType | str, record: Mapping[str, Any]) -> Any:
    return RECORD_BUILDERS.build(normalize_record_type(record_type), record)


def build_convenience(record_type: RecordType) -> Callable[[Mapping[str, Any]], Any]:
    return partial(build_record, record_type)


for _record_type in RecordType:
    globals()[f"build_{_record_type.value}_record"] = build_convenience(_record_type)


__all__ = [
    "RecordType",
    "normalize_record_type",
    "build_record",
    "build_convenience",
]
