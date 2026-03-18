from __future__ import annotations

from datetime import datetime
from datetime import timezone
from pathlib import Path

from scrapers.base.orchestration.components import JsonCheckpointRepository
from scrapers.base.orchestration.components import ParserStepExecutor
from scrapers.base.orchestration.components import SectionSourceAdapter
from scrapers.base.orchestration.components import StepAuditTrail
from scrapers.base.orchestration.models import AuditEntry
from scrapers.base.orchestration.models import AuditRepository
from scrapers.base.orchestration.models import CheckpointRepository
from scrapers.base.orchestration.models import ExecutedStep
from scrapers.base.orchestration.models import InputResolver
from scrapers.base.orchestration.models import ResolvedInput
from scrapers.base.orchestration.models import StepDeclaration
from scrapers.base.orchestration.models import StepExecutionResult
from scrapers.base.orchestration.models import StepExecutor
from scrapers.base.orchestration.models import OrchestrationPaths


class StepOrchestrator:
    def __init__(
        self,
        *,
        base_dir: Path = Path("data"),
        input_resolver: InputResolver | None = None,
        step_executor: StepExecutor | None = None,
        checkpoint_repository: CheckpointRepository | None = None,
        audit_repository: AuditRepository | None = None,
        source_adapter: SectionSourceAdapter | None = None,
        audit_trail: StepAuditTrail | None = None,
    ) -> None:
        self.paths = OrchestrationPaths(base_dir=base_dir)
        self.input_resolver = (
            input_resolver
            or source_adapter
            or SectionSourceAdapter(
                base_dir=base_dir,
            )
        )
        self.step_executor = step_executor or ParserStepExecutor()
        self.checkpoint_repository = checkpoint_repository or JsonCheckpointRepository(
            base_dir=base_dir,
        )
        self.audit_repository = (
            audit_repository
            or audit_trail
            or StepAuditTrail(
                json_path=self.paths.checkpoint_file("step_audit.json"),
                csv_path=self.paths.checkpoint_file("step_audit.csv"),
            )
        )
        self.audit_trail = self.audit_repository

    def run(self, step: StepDeclaration, domain: str) -> StepExecutionResult:
        resolved_input = self.input_resolver.resolve(step, domain)
        execution = self.step_executor.execute(step, resolved_input.records)
        output_path = self.checkpoint_repository.save(
            step=step,
            domain=domain,
            input_path=resolved_input.source_path,
            input_records=resolved_input.records,
            execution=execution,
        )
        result = self._build_result(
            step,
            domain,
            resolved_input,
            execution,
            output_path,
        )
        self.audit_repository.append(self._build_audit_entry(step, domain, result))
        if execution.errors:
            msg = f"Błąd parsera kroku {step.step_id}: {execution.errors[0]}"
            raise RuntimeError(msg)
        return result

    @staticmethod
    def _build_result(
        step: StepDeclaration,
        domain: str,
        resolved_input: ResolvedInput,
        execution: ExecutedStep,
        output_path: Path,
    ) -> StepExecutionResult:
        return StepExecutionResult(
            step=step,
            domain=domain,
            input_path=str(resolved_input.source_path),
            output_path=str(output_path),
            input_records=len(resolved_input.records),
            output_records=len(execution.records),
            errors=execution.errors,
            duration_ms=execution.duration_ms,
        )

    @staticmethod
    def _build_audit_entry(
        step: StepDeclaration,
        domain: str,
        result: StepExecutionResult,
    ) -> AuditEntry:
        return AuditEntry(
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            step_id=step.step_id,
            layer=step.layer,
            domain=domain,
            input_path=result.input_path,
            output_path=result.output_path,
            input_records=result.input_records,
            output_records=result.output_records,
            errors=result.errors,
            duration_ms=result.duration_ms,
        )
