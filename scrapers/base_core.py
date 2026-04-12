from abc import ABC

from pathlib import Path

from scrapers.abc import ScraperLifecycleABC
from scrapers.component_metadata_wiki import validate_metadata_for_component_class
from scrapers.logging import get_logger
from scrapers.options import ScraperOptions
from validation.validator_base import ExportRecord


class BaseScraperCore(ScraperLifecycleABC, ABC):
    """Minimal core with lifecycle contract and minimal state."""

    url: str

    def __init__(self, *, options: ScraperOptions) -> None:
        validate_metadata_for_component_class(type(self))
        self.include_urls = options.include_urls
        self.normalize_empty_values = options.normalize_empty_values
        self.logger = get_logger(self.__class__.__name__)
        self._run_id: str | None = options.run_id
        self.debug_dir = Path(options.debug_dir) if options.debug_dir else None
        self._validation_mode = "soft"
        self._data: list[ExportRecord] | None = None

    @property
    def validation_mode(self) -> str:
        return self._validation_mode

    @validation_mode.setter
    def validation_mode(self, value: str) -> None:
        self._validation_mode = value
