import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from scrapers.base.orchestration.components.checkpoint_payload_factory import CheckpointPayloadFactory
from scrapers.base.orchestration.models import ExecutedStep
from scrapers.base.orchestration.models import OrchestrationPaths
from scrapers.base.orchestration.models import StepDeclaration


class JsonCheckpointRepository:
    def __init__(
        self,
        *,
        base_dir: Path = Path("data"),
        payload_factory: CheckpointPayloadFactory | None = None,
    ) -> None:
        self.paths = OrchestrationPaths(base_dir=base_dir)
        self.payload_factory = payload_factory or CheckpointPayloadFactory()

    def save(
        self,
        step: StepDeclaration,
        domain: str,
        input_path: Path,
        input_records: list[dict[str, Any]],
        execution: ExecutedStep,
    ) -> Path:
        output_path = self.paths.checkpoint_file(
            f"step_{step.step_id}_{step.layer}_{domain}.json",
        )
        payload = self.payload_factory.build(
            step=step,
            domain=domain,
            input_path=input_path,
            input_records=input_records,
            execution=execution,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(asdict(payload), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_path


