from typing import Any

from scrapers.orchestration.components.base import BaseComponent
from scrapers.orchestration.stages.envelope import StageEnvelope


class BaseNormalizer(BaseComponent):
    KEY_MAP: dict[str, str] = {
        "drivers": "driver",
        "constructors": "constructor",
        "circuits": "circuit",
        "seasons": "season",
        "grands_prix": "grand_prix",
    }

    def normalize(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._normalize, payload)

    def _normalize(self, payload: StageEnvelope) -> StageEnvelope:
        return payload

    def resolve_url_row(self, domain: str, row: dict[str, Any]) -> dict[str, Any]:
        if "url" in row:
            return {"name": str(row.get("name", "")), "url": str(row.get("url", ""))}

        nested_key = self.KEY_MAP.get(domain, "")
        nested = row.get(nested_key)
        if isinstance(nested, dict):
            return {
                "name": str(nested.get("text", "")),
                "url": str(nested.get("url", "")),
            }
        return {"name": "", "url": ""}
