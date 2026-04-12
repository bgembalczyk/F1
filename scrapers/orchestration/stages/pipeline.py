from abc import ABC
from abc import abstractmethod

from scrapers.orchestration.stages.envelope import StageEnvelope


class PipelineStageABC(ABC):
    """Jednolity interfejs etapu lifecycle."""

    name: str

    @abstractmethod
    def run(self, payload: StageEnvelope) -> StageEnvelope: ...
