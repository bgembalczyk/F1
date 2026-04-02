"""DEPRECATED: use `models.contracts.contract_resolution` instead."""

from __future__ import annotations

# Deprecated shim: import from dedicated module listed below.

from models.contracts.contract_resolution import (
    CONTRACT_REGISTRY,
    resolve_record_contract,
    map_record_to_contract,
)


__all__ = [
    'CONTRACT_REGISTRY', 'resolve_record_contract', 'map_record_to_contract',
]
