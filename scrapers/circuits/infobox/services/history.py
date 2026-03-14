import re
from datetime import UTC
from datetime import datetime
from typing import Any

from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.circuits.infobox.services.constants import MONTHS
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


class CircuitHistoryParser(InfoboxTextUtils):
    """Parsowanie wydarzeń historycznych (Opened, Built, Broke ground, Former names)."""

    def _parse_former_names(
        self,
        row: dict[str, Any] | None,
    ) -> list[dict[str, Any]] | None:
        """Parsuje 'Former names' do listy dictów."""
        if not row:
            return None

        text = clean_infobox_text(row.get("text")) or ""
        if not text:
            return None

        pattern = re.compile(
            r"(?P<name>.+?)\s*\((?P<periods>[^)]*?\d[^)]*?)\)",
            flags=re.UNICODE,
        )
        matches = list(pattern.finditer(text))

        if not matches:
            cleaned = text.strip()
            return [{"name": cleaned, "periods": []}] if cleaned else None

        results: list[dict[str, Any]] = []
        for match in matches:
            name_raw = (match.group("name") or "").strip(" ;,/")
            periods_raw = (match.group("periods") or "").strip()
            if not name_raw:
                continue
            results.append(
                {
                    "name": name_raw,
                    "periods": self._parse_periods_string(periods_raw),
                },
            )

        return results or None

    def _parse_periods_string(self, periods_raw: str) -> list[dict[str, str]]:
        """Normalizuje zakresy lat do listy dictów."""
        now_year = datetime.now(tz=UTC).year
        periods: list[dict[str, str]] = []
        segments = [seg.strip() for seg in periods_raw.split(",") if seg.strip()]

        for seg in segments:
            start_raw, end_raw = self._split_period_segment(seg)
            start = self._normalize_period_endpoint(
                start_raw,
                is_start=True,
                now_year=now_year,
            )
            end = self._normalize_period_endpoint(
                end_raw,
                is_start=False,
                now_year=now_year,
            )
            if start is None and end is None:
                continue

            period: dict[str, str] = {}
            if start is not None:
                period["from"] = start
            if end is not None:
                period["to"] = end
            periods.append(period)

        return periods

    @staticmethod
    def _split_period_segment(segment: str) -> tuple[str, str]:
        if "-" in segment:
            return segment.split("-", 1)
        return segment, ""

    @staticmethod
    def _normalize_period_endpoint(
        raw: str,
        *,
        is_start: bool,
        now_year: int,
    ) -> str | None:
        """Normalizuje pojedynczy kraniec zakresu (from/to) do stringa."""
        s = (raw or "").strip()
        if not s:
            return None

        lower = s.lower()
        if not is_start and lower in {"present", "present day", "current", "now"}:
            return str(now_year)

        try:
            month_match = re.search(
                (
                    r"(january|february|march|april|may|june|july|august|"
                    r"september|october|november|december)\s+(\d{4})"
                ),
                lower,
            )
            if month_match:
                month_name = month_match.group(1)
                year = int(month_match.group(2))
                return f"{year:04d}-{MONTHS[month_name]:02d}"

            decade_match = re.search(r"(\d{4})s\b", lower)
            if decade_match:
                year = int(decade_match.group(1))
                return str(year if is_start else year + 9)

            year_match = re.search(r"(\d{4})", lower)
            if year_match:
                return str(int(year_match.group(1)))
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować zakresu daty: {raw!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc

        return None

    @staticmethod
    def _events_for_dates(
        dates_info: dict[str, Any] | None,
        first_event: str,
        followup_event: str | None = None,
    ) -> list[dict[str, Any]]:
        source = dates_info or {}
        dates = source.get("iso_dates") or source.get("years") or []
        if not dates:
            return []

        if followup_event is None:
            return [{"event": first_event, "date": date} for date in dates]

        return [
            {"event": first_event if idx == 0 else followup_event, "date": date}
            for idx, date in enumerate(dates)
        ]

    def parse_history(
        self,
        rows: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        events = [
            *self._events_for_dates(
                self._parse_dates(rows.get("opened")),
                "opened",
                "reopened",
            ),
            *self._events_for_dates(self._parse_dates(rows.get("closed")), "closed"),
            *self._events_for_dates(
                self._parse_dates(rows.get("broke_ground")),
                "broke_ground",
            ),
            *self._events_for_dates(self._parse_dates(rows.get("built")), "built"),
        ]
        events = sorted(events, key=lambda event: event.get("date") or "")

        return {
            "events": events or None,
            "former_names": self._parse_former_names(rows.get("former_names")),
        }
