from typing import Any
from typing import Dict
from typing import Mapping
from typing import TypeAlias

RawRecord: TypeAlias = Dict[str, Any]
NormalizedRecord: TypeAlias = Dict[str, Any]


def record_from_mapping(record: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(record)
