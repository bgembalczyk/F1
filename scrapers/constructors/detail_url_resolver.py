from typing import Any

from scrapers.base.detail_url_resolver import DetailUrlResolver
from scrapers.base.detail_url_resolver import resolve_first_valid_detail_url


class ConstructorDetailUrlResolver(DetailUrlResolver):
    """Resolve constructor detail URL across heterogeneous list schemas."""

    _CANDIDATE_KEYS = (
        "constructor.url",
        "constructor_url",
        "team_url",
    )

    def resolve(self, record: dict[str, Any]) -> str | None:
        return resolve_first_valid_detail_url(record, candidate_keys=self._CANDIDATE_KEYS)
