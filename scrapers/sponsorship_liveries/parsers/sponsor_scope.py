from typing import Any
from typing import Dict

from scrapers.sponsorship_liveries.parsers.grand_prix_scope import (
    GrandPrixScopeParser,
)
from scrapers.sponsorship_liveries.parsers.record_text import (
    SponsorshipRecordText,
)


class SponsorScopeHandler:
    @staticmethod
    def filter_sponsors_for_year(sponsors: Any, year: int) -> Any:
        if not isinstance(sponsors, list):
            return sponsors
        filtered: list[Any] = []
        for item in sponsors:
            if isinstance(item, dict):
                params = item.get("params") or []
                if not GrandPrixScopeParser.params_contain_only_years_or_grand_prix(
                        params,
                ):
                    cleaned_item = {k: v for k, v in item.items() if k != "params"}
                    filtered.append(cleaned_item)
                    continue
                year_params = SponsorshipRecordText.extract_year_params(params)
                if not year_params or year in year_params:
                    cleaned_params = [
                        param
                        for param in params
                        if not SponsorshipRecordText.is_year_param(param)
                    ]
                    if cleaned_params:
                        filtered.append({**item, "params": cleaned_params})
                    else:
                        cleaned_item = {k: v for k, v in item.items() if k != "params"}
                        filtered.append(cleaned_item)
                continue
            filtered.append(item)
        return filtered

    @staticmethod
    def record_has_year_specific_sponsors(
            record: Dict[str, Any], sponsor_keys: set[str],
    ) -> bool:
        for key in sponsor_keys:
            sponsors = record.get(key)
            if not isinstance(sponsors, list):
                continue
            for item in sponsors:
                if not isinstance(item, dict):
                    continue
                params = item.get("params") or []
                if not GrandPrixScopeParser.params_contain_only_years_or_grand_prix(
                        params,
                ):
                    continue
                if SponsorshipRecordText.extract_year_params(params):
                    return True
        return False
