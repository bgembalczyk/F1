from typing import Any

from scrapers.base.detail_url_resolver import DetailUrlResolver
from scrapers.base.detail_url_resolver import resolve_first_valid_detail_url


class SeasonDetailUrlResolver(DetailUrlResolver):
    _CANDIDATE_KEYS = ("season.url",)

    def resolve(self, record: dict[str, Any]) -> str | None:
        return resolve_first_valid_detail_url(record, candidate_keys=self._CANDIDATE_KEYS)
