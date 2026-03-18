from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CompleteExtractorDomainConfig:
    """Konfiguracja domeny dla CompleteExtractorBase.

    Jak dodać nową domenę bez kopiowania klasy:
    1) ustaw `list_scraper_cls` i `single_scraper_cls`,
    2) ustaw `detail_url_field_path` (np. ``"driver.url"``),
    3) opcjonalnie dopasuj `assemble_record_strategy` i parametry,
    4) opcjonalnie dodaj `record_postprocessor`, gdy wynik wymaga finalnej normalizacji.

    Dzięki temu nowy extractor często ogranicza się do kilku atrybutów klasowych.
    """

    list_scraper_cls: type[Any] | None = None
    single_scraper_cls: type[Any] | None = None
    detail_url_field_path: str | None = None
    assemble_record_strategy: str = "attach_details"
    assemble_record_params: dict[str, Any] | None = None
    record_postprocessor: Callable[[dict[str, Any]], dict[str, Any]] | None = None
