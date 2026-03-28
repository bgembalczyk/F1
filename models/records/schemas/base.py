from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import is_dataclass
from typing import Any
from typing import ClassVar


@dataclass(frozen=True)
class ExportSchemaModel:
    """Shared base for scraper export models with contract validation."""

    contract_fields: ClassVar[tuple[str, ...]] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("contract_fields", None)
        return payload

    def missing_contract_fields(self) -> list[str]:
        payload = self.to_dict()
        missing: list[str] = []
        for field in self.contract_fields:
            value = payload.get(field)
            if value is None:
                missing.append(field)
                continue
            if isinstance(value, str) and not value.strip():
                missing.append(field)
                continue
            if isinstance(value, list) and not value:
                missing.append(field)
                continue
            if isinstance(value, dict) and not value:
                missing.append(field)
        return missing


def serialize_model(value: Any) -> Any:
    if isinstance(value, ExportSchemaModel):
        return {k: serialize_model(v) for k, v in value.to_dict().items()}
    if is_dataclass(value):
        return {k: serialize_model(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: serialize_model(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [serialize_model(item) for item in value]
    return value
