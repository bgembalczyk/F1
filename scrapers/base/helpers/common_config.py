from dataclasses import dataclass

from models.value_objects.enums import ValidationMode


@dataclass(frozen=True)
class ScraperCommonConfig:
    include_urls: bool = True
    normalize_empty_values: bool = True
    validation_mode: str | ValidationMode = ValidationMode.SOFT

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "validation_mode",
            ValidationMode.from_raw(self.validation_mode),
        )
