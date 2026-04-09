from dataclasses import dataclass

from scrapers.orchestration.checkpoint.metrics import CheckpointMetrics


@dataclass(frozen=True)
class CheckpointMetadata:
    step_id: int
    layer: str
    domain: str
    input_source: str
    output_target: str
    parser: str
    generated_at: str
    metrics: CheckpointMetrics
