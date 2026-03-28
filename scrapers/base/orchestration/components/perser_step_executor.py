import time
from typing import Any

from scrapers.base.orchestration.models import ExecutedStep
from scrapers.base.orchestration.models import StepDeclaration

PARSER_STEP_EXCEPTIONS = (TypeError, ValueError, KeyError, AttributeError)


class ParserStepExecutor:
    def execute(
        self,
        step: StepDeclaration,
        input_records: list[dict[str, Any]],
    ) -> ExecutedStep:
        started_at = time.perf_counter()
        errors: list[str] = []
        try:
            output_records = step.parser(input_records)
        except PARSER_STEP_EXCEPTIONS as exc:
            output_records = []
            errors.append(str(exc))
        return ExecutedStep(
            records=output_records,
            errors=errors,
            duration_ms=(time.perf_counter() - started_at) * 1000,
        )
