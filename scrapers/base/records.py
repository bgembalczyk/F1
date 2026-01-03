from typing import Any, Dict, Mapping, TypeAlias

RawRecord: TypeAlias = Dict[str, Any]
NormalizedRecord: TypeAlias = Dict[str, Any]
ExportRecord: TypeAlias = Dict[str, Any]


def record_from_mapping(record: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(record)
