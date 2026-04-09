from dataclasses import dataclass
from typing import Any

from scrapers.orchestration.checkpoint.metadata import CheckpointMetadata


@dataclass(frozen=True)
class CheckpointPayload:
    metadata: CheckpointMetadata
    records: list[dict[str, Any]]
