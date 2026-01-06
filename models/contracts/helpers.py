from typing import Any
from typing import Mapping

from models.contracts.base import DataContract
from models.contracts.circuit import CircuitContract
from models.contracts.driver import DriverContract
from models.contracts.points import POINTS_KEYS
from models.contracts.points import PointsContract


def is_points_record(record: Mapping[str, Any]) -> bool:
    if "seasons" not in record:
        return False
    return any(key in record for key in POINTS_KEYS)


def map_record_to_contract(
    record: Mapping[str, Any],
) -> DataContract | Mapping[str, Any]:
    if "driver" in record and (
        "is_active" in record or "drivers_championships" in record
    ):
        return DriverContract.from_record(record)
    if "circuit" in record and "circuit_status" in record:
        return CircuitContract.from_record(record)
    if is_points_record(record):
        return PointsContract.from_record(record)
    return record
