from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IndianapolisOnlyListConfig:
    """Declarative configuration for Indianapolis 500 only list scrapers."""

    url: str
    record_key: str
    url_key: str
    domain_name: str | None = None
    record_type: str | None = None
