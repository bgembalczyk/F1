from typing import Protocol

from scrapers.orchestration.stages.envelope import StageEnvelope


class PipelineStage(Protocol):
    """Jednolity interfejs etapu lifecycle."""

    name: str

    def run(self, payload: StageEnvelope) -> StageEnvelope: ...
