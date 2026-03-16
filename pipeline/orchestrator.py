from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone

SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class PipelineStep:
    step_id: str
    input_source: str
    parser: str
    output_path: str
    runner: object

    def run(self) -> None:
        self.runner()


@dataclass(frozen=True)
class Layer0Step(PipelineStep):
    """Warstwa 0: listy i podstawowe ekstrakcje."""


@dataclass(frozen=True)
class Layer1Step(PipelineStep):
    """Warstwa 1: dane kompletne i agregacje."""


class PipelineOrchestrator:
    def __init__(
        self,
        steps: list[PipelineStep],
        checkpoint_dir,
        schema_version: str = SCHEMA_VERSION,
    ) -> None:
        self._steps = steps
        self._checkpoint_dir = checkpoint_dir
        self._schema_version = schema_version

    def run(self) -> None:
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
        for step in self._steps:
            step.run()
            self._write_checkpoint(step)

    def _write_checkpoint(self, step: PipelineStep):
        checkpoint = {
            "step_id": step.step_id,
            "input_source": step.input_source,
            "parser": step.parser,
            "output_path": step.output_path,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "schema_version": self._schema_version,
        }
        checkpoint_path = self._checkpoint_dir / f"{step.step_id}.json"
        checkpoint_path.write_text(
            json.dumps(checkpoint, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return checkpoint_path
