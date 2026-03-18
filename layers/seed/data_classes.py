from collections.abc import Callable
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Any

from scrapers.wiki.contants import SEED_RECORD_SCHEMA_VERSION


@dataclass(frozen=True)
class RegistryValidationRule:
    label: str
    extractor: Callable[[Any], str]
    expected_prefix: Callable[[Any], str]
    message: Callable[[Any], str]


@dataclass(frozen=True)
class RegistryValidationSpec:
    duplicate_message: Callable[[str], str]
    empty_url_message: Callable[[str], str]
    path_rules: tuple[RegistryValidationRule, ...]


@dataclass(frozen=True)
class SeedRecord:
    schema_version: str
    name: str
    link: str | None
    source_url: str
    scraped_at: str

    @classmethod
    def from_raw(
        cls,
        raw: dict[str, Any],
        *,
        source_url: str,
        scraped_at: datetime,
        schema_version: str = SEED_RECORD_SCHEMA_VERSION,
    ) -> "SeedRecord":
        from layers.seed.helpers import _extract_link
        from layers.seed.helpers import _extract_name

        return cls(
            schema_version=schema_version,
            name=_extract_name(raw),
            link=_extract_link(raw),
            source_url=source_url,
            scraped_at=scraped_at.astimezone(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SeedQualityReport:
    seed_name: str
    category: str
    records_count: int
    empty_name_count: int
    empty_link_count: int
    duplicate_name_count: int

    def to_log_line(self) -> str:
        return (
            "[seed-quality] "
            f"seed={self.seed_name} "
            f"category={self.category} "
            f"records={self.records_count} "
            f"empty_name={self.empty_name_count} "
            f"empty_link={self.empty_link_count} "
            f"duplicate_name={self.duplicate_name_count}"
        )
