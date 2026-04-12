from scrapers.orchestration.components.base import BaseComponent
from scrapers.orchestration.stages.envelope import StageEnvelope


class BaseOrchestrator(BaseComponent):
    def execute(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._execute, payload)

    def _execute(self, payload: StageEnvelope) -> StageEnvelope:
        return payload
