import re
from typing import Any

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText


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
    def parse_grand_prix_scope(
        cls,
        params: list[Any],
    ) -> dict[str, Any] | None:
        if not params or not cls.params_contain_only_years_or_grand_prix(params):
            return None

        parsed = _GrandPrixScopeAccumulator()
        for param in params:
            cls._consume_scope_param(parsed, param)
            if parsed.invalid:
                return None

        return parsed.build_scope()

    @classmethod
    def _consume_scope_param(
        cls,
        parsed: "_GrandPrixScopeAccumulator",
        param: Any,
    ) -> None:
        if SponsorshipRecordText.is_year_param(param):
            return
        text = SponsorshipRecordText.param_text(param)
        if not re.search(r"grand prix", text, flags=re.IGNORECASE):
            parsed.invalid = True
            return
        if re.search(r"\bonwards?\b", text, flags=re.IGNORECASE):
            parsed.has_onwards = True

        range_scope = cls._build_range_scope_from_text(param, text)
        if range_scope is not None:
            parsed.range_scope = range_scope
            return

        cleaned = SponsorshipRecordText.clean_grand_prix_text(text)
        if cleaned:
            parsed.entries.append(cls.build_grand_prix_entry(param, cleaned))

    @classmethod
    def _build_range_scope_from_text(
        cls,
        param: Any,
        text: str,
    ) -> dict[str, Any] | None:
        range_match = re.search(
            r"(.+?grand prix)\s+to\s+(.+?grand prix)",
            text,
            flags=re.IGNORECASE,
        )
        if not range_match:
            return None
        start_text = SponsorshipRecordText.clean_grand_prix_text(range_match.group(1))
        end_text = SponsorshipRecordText.clean_grand_prix_text(range_match.group(2))
        return {
            "type": "range",
            "from": cls.build_grand_prix_entry(param, start_text),
            "to": cls.build_grand_prix_entry(param, end_text),
        }

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
            clean_wiki_text(text),
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


class _GrandPrixScopeAccumulator:
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.has_onwards = False
        self.range_scope: dict[str, Any] | None = None
        self.invalid = False

    def build_scope(self) -> dict[str, Any] | None:
        if self.range_scope:
            return self.range_scope
        if self.has_onwards and self.entries:
            return {"type": "range", "from": self.entries[0], "to": None}
        if self.entries:
            return {"type": "only", "grand_prix": self.entries}
        return None
