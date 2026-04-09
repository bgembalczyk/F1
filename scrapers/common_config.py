from dataclasses import dataclass


@dataclass(frozen=True)
class ScraperCommonConfig:
    include_urls: bool = True
    normalize_empty_values: bool = True
    validation_mode: str = "soft"
