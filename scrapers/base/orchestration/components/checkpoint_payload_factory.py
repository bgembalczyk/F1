import datetime
from typing import Any

from pathlib import Path

from scrapers.base.orchestration.models import CheckpointMetadata
from scrapers.base.orchestration.models import CheckpointMetrics
from scrapers.base.orchestration.models import CheckpointPayload
from scrapers.base.orchestration.models import ExecutedStep
from scrapers.base.orchestration.models import StepDeclaration


class CheckpointPayloadFactory:
    def build(
        self,
        *,
        step: StepDeclaration,
        domain: str,
        input_path: Path,
        input_records: list[dict[str, Any]],
        execution: ExecutedStep,
    ) -> CheckpointPayload:
        return CheckpointPayload(
            metadata=CheckpointMetadata(
                step_id=step.step_id,
                layer=step.layer,
                domain=domain,
                input_source=str(input_path),
                output_target=step.output_target,
                parser=step.parser.__name__,
                generated_at=datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
                metrics=CheckpointMetrics(
                    input_records=len(input_records),
                    output_records=len(execution.records),
                    errors=len(execution.errors),
                    duration_ms=execution.duration_ms,
                    input_path=str(input_path),
                ),
            ),
            records=execution.records,
        )


