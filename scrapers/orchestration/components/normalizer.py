from scrapers.orchestration.components.base import BaseComponent
from scrapers.orchestration.stages.envelope import StageEnvelope


class BaseNormalizer(BaseComponent):
    def normalize(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._normalize, payload)

    def _normalize(self, payload: StageEnvelope) -> StageEnvelope:
        return payload
