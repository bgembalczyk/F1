from scrapers.orchestration import BaseComponent
from scrapers.orchestration.stages.envelope import StageEnvelope


class BaseExtractor(BaseComponent):
    def extract(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._extract, payload)

    def _extract(self, payload: StageEnvelope) -> StageEnvelope:
        return payload
