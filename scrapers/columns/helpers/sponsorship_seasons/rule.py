from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    name: str
    condition: Callable[["RuleContext"], bool]
    effect: Callable[["RuleContext"], bool]
