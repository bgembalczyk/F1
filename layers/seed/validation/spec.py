from dataclasses import dataclass
from typing import Callable

from layers.seed.validation.rule import RegistryValidationRule


@dataclass(frozen=True)
class RegistryValidationSpec:
    duplicate_message: Callable[[str], str]
    empty_url_message: Callable[[str], str]
    path_rules: tuple[RegistryValidationRule, ...]
