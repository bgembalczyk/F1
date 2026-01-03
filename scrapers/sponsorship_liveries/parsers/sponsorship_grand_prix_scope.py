import re
from typing import Any

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.sponsorship_liveries.parsers.sponsorship_record_text import (
    SponsorshipRecordText,
)


class GrandPrixScopeParser:
    @classmethod
    def params_contain_only_years_or_grand_prix(cls, params: list[Any]) -> bool:
        if not params:
            return True
        for param in params:
            text = SponsorshipRecordText.param_text(param)
            if SponsorshipRecordText.is_year_param(param):
                continue
            if re.search(r"grand prix", text, flags=re.IGNORECASE):
                continue
            return False
        return True

    @classmethod
    def parse_grand_prix_scope(cls, params: list[Any]) -> dict[str, Any] | None:
        if not params:
            return None
        if not cls.params_contain_only_years_or_grand_prix(params):
            return None
        grand_prix_entries: list[dict[str, Any]] = []
        has_onwards = False
        range_scope: dict[str, Any] | None = None
        for param in params:
            if SponsorshipRecordText.is_year_param(param):
                continue
            text = SponsorshipRecordText.param_text(param)
            if not re.search(r"grand prix", text, flags=re.IGNORECASE):
                return None
            if re.search(r"\bonwards?\b", text, flags=re.IGNORECASE):
                has_onwards = True
            range_match = re.search(
                r"(.+?grand prix)\s+to\s+(.+?grand prix)",
                text,
                flags=re.IGNORECASE,
            )
            if range_match:
                start_text = SponsorshipRecordText.clean_grand_prix_text(
                    range_match.group(1)
                )
                end_text = SponsorshipRecordText.clean_grand_prix_text(
                    range_match.group(2)
                )
                range_scope = {
                    "type": "range",
                    "from": cls.build_grand_prix_entry(param, start_text),
                    "to": cls.build_grand_prix_entry(param, end_text),
                }
                continue
            cleaned = SponsorshipRecordText.clean_grand_prix_text(text)
            if not cleaned:
                continue
            grand_prix_entries.append(cls.build_grand_prix_entry(param, cleaned))

        if range_scope:
            return range_scope
        if has_onwards and grand_prix_entries:
            return {
                "type": "range",
                "from": grand_prix_entries[0],
                "to": None,
            }
        if grand_prix_entries:
            return {"type": "only", "grand_prix": grand_prix_entries}
        return None

    @staticmethod
    def build_grand_prix_entry(param: Any, text: str) -> dict[str, Any]:
        if isinstance(param, dict) and param.get("url"):
            return {"text": text, "url": param["url"]}
        return {"text": text}

    @staticmethod
    def parse_grand_prix_names(text: str) -> list[str]:
        text = re.sub(r"\bGrands Prix\b", "Grand Prix", text, flags=re.IGNORECASE)
        text = re.sub(r"\bGrand Prix\b", "", text, flags=re.IGNORECASE).strip()
        if text:
            parts = re.split(r"\s*(?:,| and )\s*", text)
            return [f"{part.strip()} Grand Prix" for part in parts if part.strip()]
        matches = re.findall(r"[^,;]+?Grand Prix", text, flags=re.IGNORECASE)
        return [clean_wiki_text(match) for match in matches if match.strip()] or [
            clean_wiki_text(text)
        ]

    @staticmethod
    def grand_prix_scope_key(scope: dict[str, Any]) -> tuple[Any, ...]:
        scope_type = scope.get("type")
        if scope_type == "only":
            entries = scope.get("grand_prix") or []
            key_entries = []
            for entry in entries:
                if isinstance(entry, dict):
                    key_entries.append((entry.get("text"), entry.get("url")))
                else:
                    key_entries.append((str(entry), None))
            return ("only", tuple(key_entries))
        if scope_type == "range":
            start = scope.get("from") or {}
            end = scope.get("to") or {}
            return (
                "range",
                start.get("text"),
                start.get("url"),
                end.get("text"),
                end.get("url"),
            )
        return ("other",)
