from dataclasses import dataclass


@dataclass(frozen=True)
class MetricColumnSpec:
    header: str
    output_key: str
    metric_key: str
