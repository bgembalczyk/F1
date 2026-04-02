from __future__ import annotations

from scrapers.wiki.constants import TYRE_MANUFACTURERS_SOURCE

from .base import DomainTransformStrategy


class TyreManufacturersTransformStrategy(DomainTransformStrategy):
    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        transformed = dict(record)
        if source_name != TYRE_MANUFACTURERS_SOURCE:
            return transformed

        if "manufacturers" in transformed:
            transformed["tyre_manufacturers"] = transformed.pop("manufacturers")
        seasons = transformed.get("seasons")
        if isinstance(seasons, list) and len(seasons) == 1:
            transformed["season"] = transformed.pop("seasons")[0]
        return transformed
