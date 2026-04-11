from scrapers.orchestration import BaseComponent
from scrapers.orchestration.stages.envelope import StageEnvelope


class BaseParsingStage(BaseComponent):
    def run(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._run, payload)

    def _run(self, payload: StageEnvelope) -> StageEnvelope:
        return payload
