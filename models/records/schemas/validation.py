from __future__ import annotations

import logging

from models.records.schemas.base import ExportSchemaModel


def validate_model_contract(
    model: ExportSchemaModel,
    *,
    logger: logging.Logger,
) -> None:
    missing = model.missing_contract_fields()
    if not missing:
        return
    logger.warning(
        "Brakujące pola kontraktowe dla %s: %s",
        model.__class__.__name__,
        ", ".join(sorted(missing)),
    )
