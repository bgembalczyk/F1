from scrapers.list.indianapolis_only.config import IndianapolisOnlyListConfig


class IndianapolisOnlyMixin:
    """Shared configuration mixin for Indianapolis 500 only list scrapers."""

    section_id = "Indianapolis_500_only"
    domain_name: str | None = None
    record_type: str | None = None
    CONFIG: IndianapolisOnlyListConfig | None = None
