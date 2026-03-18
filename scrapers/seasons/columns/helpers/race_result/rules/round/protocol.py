from typing import Any
from typing import Protocol

from scrapers.seasons.columns.helpers.race_result.rules.round.context import (
    RoundRuleContext,
)


class RoundRule(Protocol):
    def apply(self, context: RoundRuleContext) -> dict[str, Any] | None: ...
