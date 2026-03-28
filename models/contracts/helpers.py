import logging
from collections.abc import Mapping
from typing import Any

from models.contracts.base import DataContract
from models.contracts.base import RecordContract
from models.contracts.circuit import CircuitContract
from models.contracts.driver import DriverContract
from models.contracts.points import PointsContract

logger = logging.getLogger(__name__)

CONTRACT_REGISTRY: tuple[type[RecordContract], ...] = (
    DriverContract,
    CircuitContract,
    PointsContract,
)


def resolve_record_contract(
    record: Mapping[str, Any],
) -> type[RecordContract] | None:
    matches = [
        contract for contract in CONTRACT_REGISTRY if contract.can_handle(record)
    ]
    if not matches:
        return None

    if len(matches) > 1:
        logger.warning(
            "Niejednoznaczne dopasowanie kontraktu dla kluczy=%s. "
            "Używam fallbacku do pierwszego kontraktu: %s",
            sorted(record.keys()),
            matches[0].__name__,
        )
    return matches[0]


def map_record_to_contract(
    record: Mapping[str, Any],
) -> DataContract | Mapping[str, Any]:
    resolved_contract = resolve_record_contract(record)
    if resolved_contract is None:
        logger.debug(
            "Brak dopasowania kontraktu dla kluczy=%s, zwracam surowy rekord.",
            sorted(record.keys()),
        )
        return record
    return resolved_contract.from_record(record)
