from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RegistryValidationRule:
    label: str
    extractor: Callable[[Any], str]
    expected_prefix: Callable[[Any], str]
    message: Callable[[Any], str]
