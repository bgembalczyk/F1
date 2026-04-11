import json
from pathlib import Path
from typing import Any


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
