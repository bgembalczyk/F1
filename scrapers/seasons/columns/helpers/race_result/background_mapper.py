import re

from scrapers.seasons.columns.helpers.constants import SHORT_HEX_COLOR_LENGTH


class RaceResultBackgroundMapper:
    def __init__(self, background_to_result: dict[str, str]) -> None:
        self._background_to_result = background_to_result

    def map(self, background: str | None) -> str | None:
        normalized = self._normalize_background(background)
        if normalized is None:
            return None
        return self._background_to_result.get(normalized)

    def _normalize_background(self, background: str | None) -> str | None:
        if not background:
            return None
        match = re.search(r"#?([0-9a-f]{6}|[0-9a-f]{3})", background, re.IGNORECASE)
        if not match:
            return None
        return self._expand_short_hex(match.group(1).lower())

    @staticmethod
    def _expand_short_hex(value: str) -> str:
        if len(value) == SHORT_HEX_COLOR_LENGTH:
            return "".join(char * 2 for char in value)
        return value
