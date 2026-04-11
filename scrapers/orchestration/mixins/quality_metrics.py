from typing import Any


class QualityMetricsMixin:
    def build_stage_metrics(
        self,
        *,
        input_records: int,
        output_records: int,
        errors: list[str],
    ) -> dict[str, Any]:
        return {
            "input_records": input_records,
            "output_records": output_records,
            "errors": len(errors),
        }
