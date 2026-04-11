from scrapers.orchestration import BaseComponent
from scrapers.orchestration.stages.envelope import StageEnvelope


class BaseParser(BaseComponent):
    def parse(self, payload: StageEnvelope) -> StageEnvelope:
        return self.run_with_lifecycle(self._parse, payload)

    def _parse(self, payload: StageEnvelope) -> StageEnvelope:
        return payload
