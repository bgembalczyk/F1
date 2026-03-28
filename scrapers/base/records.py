from collections.abc import Mapping
from typing import Any
from typing import TypeAlias

from scrapers.base.factory.record_factory import RECORD_FACTORIES

RawRecord: TypeAlias = dict[str, Any]
NormalizedRecord: TypeAlias = dict[str, Any]


def record_from_mapping(record: Mapping[str, Any]) -> dict[str, Any]:
    """Legacy helper kept for compatibility; delegates to RecordFactory adapter."""
    return RECORD_FACTORIES.mapping().create(record)
