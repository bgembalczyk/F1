from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scrapers.orchestration.base_component import BaseComponent
from scrapers.orchestration.stages.envelope import StageEnvelope


class UrlResolverMixin:
    KEY_MAP: dict[str, str] = {
        "drivers": "driver",
        "constructors": "constructor",
        "circuits": "circuit",
        "seasons": "season",
        "grands_prix": "grand_prix",
    }

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


class QualityMetricsMixin:
    def build_stage_metrics(
        self, *, input_records: int, output_records: int, errors: list[str]
    ) -> dict[str, Any]:
        return {
            "input_records": input_records,
            "output_records": output_records,
            "errors": len(errors),
        }


class CheckpointIOWithFallbackMixin:
    def read_records_with_fallback(
        self,
        *,
        checkpoints_dir: Path,
        raw_dir: Path,
        input_source: str,
        domain: str,
        layer: str,
    ) -> tuple[list[dict[str, Any]], Path]:
        checkpoint_candidates = [
            checkpoints_dir / f"{input_source}.json",
            checkpoints_dir / f"step_0_layer0_{domain}.json",
            checkpoints_dir / f"step_1_{layer}_{domain}.json",
        ]
        raw_candidates = [
            raw_dir / f"{input_source}.json",
            raw_dir / domain / f"{input_source}.json",
            raw_dir / domain / f"{domain}.json",
        ]
        for path in checkpoint_candidates + raw_candidates:
            if path.exists():
                return self._load_records(path), path
        msg = f"Missing checkpoint/raw input for domain={domain}, source={input_source}"
        raise FileNotFoundError(msg)

    def write_checkpoint_payload(
        self,
        *,
        output_path: Path,
        metadata: dict[str, Any],
        records: list[dict[str, Any]],
        errors: list[str],
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                {
                    "metadata": metadata,
                    "records": records,
                    "errors": errors,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _load_records(path: Path) -> list[dict[str, Any]]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            records = payload.get("records", payload.get("items", []))
            if isinstance(records, list):
                return [row for row in records if isinstance(row, dict)]
            return []
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        return []


class BaseExtractor(BaseComponent):
    def extract(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._extract, payload)

    def _extract(self, payload: StageEnvelope) -> StageEnvelope:
        return payload


class BaseParser(BaseComponent):
    def parse(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._parse, payload)

    def _parse(self, payload: StageEnvelope) -> StageEnvelope:
        return payload


class BaseNormalizer(BaseComponent):
    def normalize(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._normalize, payload)

    def _normalize(self, payload: StageEnvelope) -> StageEnvelope:
        return payload


class BaseOrchestrator(BaseComponent):
    def execute(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._execute, payload)

    def _execute(self, payload: StageEnvelope) -> StageEnvelope:
        return payload


__all__ = [
    "BaseExtractor",
    "BaseParser",
    "BaseNormalizer",
    "BaseOrchestrator",
    "UrlResolverMixin",
    "QualityMetricsMixin",
    "CheckpointIOWithFallbackMixin",
]
