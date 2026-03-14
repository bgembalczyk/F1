from collections.abc import Mapping
from typing import Any
from typing import TypeAlias

RawRecord: TypeAlias = dict[str, Any]
NormalizedRecord: TypeAlias = dict[str, Any]


def record_from_mapping(record: Mapping[str, Any]) -> dict[str, Any]:
    return dict(record)
