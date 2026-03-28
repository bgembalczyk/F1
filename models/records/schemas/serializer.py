from __future__ import annotations

from typing import Any

from models.records.schemas.base import serialize_model


def serialize_for_json(value: Any) -> Any:
    return serialize_model(value)
