from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Rule:
    name: str
    condition: Callable[["RuleContext"], bool]
    effect: Callable[["RuleContext"], bool]


