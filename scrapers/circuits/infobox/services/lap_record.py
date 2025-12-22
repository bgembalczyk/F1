import re
from typing import Any, Dict, List, Optional, Tuple

from models.records import LinkRecord
from models.services.circuits.lap_record_utils import (
    build_lap_record_key,
    normalize_lap_record_entity,
)
from models.services.circuits.lap_record_merging import (
    merge_two_records,
    normalize_lap_record,
)
from scrapers.base.helpers.time import parse_time_seconds_from_text
from scrapers.base.helpers.wiki import is_wikipedia_redlink
from scrapers.circuits.infobox.services.text_processing import CircuitTextProcessing


def extract_time(text: str) -> Optional[float]:
    if not text:
        return None

    head = text.split("(", 1)[0].strip()
    time_match = re.match(r"^\s*(\d+:\d{2}(?:\.\d+)?)\b", head)
    time_str = time_match.group(1) if time_match else None

    sec = parse_time_seconds_from_text(time_str) if time_str else None

    if sec is None:
        m = re.search(r"\b(\d+:\d{2}(?:\.\d+)?)\b", text)
        if m:
            sec = parse_time_seconds_from_text(m.group(1))

    return sec


def select_details_paren(text: str) -> list[str]:
    parens = re.findall(r"\(([^)]*)\)", text or "")
    if not parens:
        return []

    def _is_speed_paren(s: str) -> bool:
        s_low = s.lower()
        return ("km/h" in s_low) or ("mph" in s_low)

    def _score_details_candidate(s: str) -> int:
        if not s:
            return -10
        if _is_speed_paren(s):
            return -100

        parts = [p.strip() for p in s.split(",") if p.strip()]
        score = 0

        if len(parts) >= 4:
            score += 5
        elif len(parts) == 3:
            score += 2
        elif len(parts) == 2:
            score += 1
        else:
            score -= 2

        if any(re.fullmatch(r"\d{4}", p) for p in parts):
            score += 5

        if "," not in s and score < 3:
            score -= 3

        return score

    best = max(parens, key=_score_details_candidate)
    if _score_details_candidate(best) <= 0:
        return []

    return [p.strip() for p in best.split(",") if p.strip()]


class CircuitLapRecordParser(CircuitTextProcessing):
    """Logika parsowania, porównywania i scalania lap record'ów."""

    def _wrap_entity_from_links(
        self, entity_text: Optional[str], links: List[LinkRecord]
    ) -> Optional[Dict[str, Any]]:
        if not entity_text:
            return None

        cleaned = self._strip_lang_markers(entity_text).strip()
        cleaned = self._strip_lang_marker_tail_only(cleaned).strip()
        if not cleaned:
            return None

        obj: Dict[str, Any] = {"text": cleaned, "url": None}

        link = self._find_link(cleaned, links) if links else None

        if not link and "/" in cleaned:
            for part in [p.strip() for p in cleaned.split("/") if p.strip()]:
                link = self._find_link(part, links)
                if link:
                    break

        if link:
            url = link.get("url")
            if url and not is_wikipedia_redlink(url) and self._is_en_wiki(url):
                obj["url"] = url

        return obj

    def parse_lap_record(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Parsuje pojedynczą komórkę "Race lap record" z infoboksa.
        """
        if not row:
            return None

        text = self._get_text(row) or ""
        if not text:
            return None

        links = row.get("links") or []
        sec = extract_time(text)
        details = select_details_paren(text)

        if not details:
            return None

        record = self.build_lap_record(details, links, sec)
        return record or None

    def build_lap_record(
        self, details: List[str], links: List[LinkRecord], time: Optional[float]
    ) -> Dict[str, Any]:
        record: Dict[str, Any] = {}
        if time is not None:
            record["time"] = time

        driver_text = details[0] if len(details) >= 1 else None
        car_text = details[1] if len(details) >= 2 else None
        year_text = details[2] if len(details) >= 3 else None
        series_text = details[3] if len(details) >= 4 else None

        record.update(
            {
                "driver": self._wrap_entity_from_links(driver_text, links),
                "vehicle": self._wrap_entity_from_links(car_text, links),
                "year": year_text,
                "series": self._wrap_entity_from_links(series_text, links)
                if series_text
                else None,
            }
        )

        record = self.prune_nulls(record) or {}
        normalize_lap_record(record)

        if not any(record.get(k) for k in ("driver", "vehicle", "year", "series")):
            return {}

        return record

    @staticmethod
    def _year_from_record(rec: Dict[str, Any]) -> Optional[str]:
        y = rec.get("year")
        if y:
            return str(y).strip()

        d = rec.get("date")
        if isinstance(d, str) and len(d) >= 4 and d[:4].isdigit():
            return d[:4]

        ev = rec.get("event")
        ev_txt = ev.get("text") if isinstance(ev, dict) else (str(ev) if ev else "")
        ev_txt = (ev_txt or "").strip()
        if len(ev_txt) >= 4 and ev_txt[:4].isdigit():
            return ev_txt[:4]

        return None

    def _lap_record_key(
        self, rec: Dict[str, Any]
    ) -> Optional[Tuple[str, str, int, str]]:
        sanitizer = self._strip_lang_marker_tail_only
        return build_lap_record_key(
            rec,
            year_extractor=self._year_from_record,
            vehicle_getter=self._get_vehicle_field,
            time_extractor=lambda r: parse_time_seconds_from_text(r.get("time")),
            driver_normalizer=lambda value: normalize_lap_record_entity(
                value, sanitizer=sanitizer
            ),
            vehicle_normalizer=lambda value: normalize_lap_record_entity(
                value, sanitizer=sanitizer
            ),
            time_key_factory=lambda sec: int(round(sec * 1000)),
            key_order=("driver", "vehicle", "time", "year"),
        )

    def same_lap_record(self, left: dict, right: dict) -> bool:
        if not left or not right:
            return False
        kl = self._lap_record_key(left)
        kr = self._lap_record_key(right)
        return bool(kl and kr and kl == kr)

    def _find_lap_record(
        self, candidate: Dict[str, Any], records: List[Dict[str, Any]]
    ) -> Optional[Tuple[int, Dict[str, Any]]]:
        cand_key = self._lap_record_key(candidate)
        if cand_key is None:
            return None

        for i, record in enumerate(records):
            existing = record.get("race_lap_record")
            if not existing:
                continue
            if self._lap_record_key(existing) == cand_key:
                return i, existing

        return None

    def merge_lap_record(
        self, existing: Dict[str, Any], candidate: Dict[str, Any]
    ) -> Dict[str, Any]:
        normalize_lap_record(existing)
        normalize_lap_record(candidate)
        merged = merge_two_records(existing, candidate)
        return self.prune_nulls(merged)

    def _upsert_lap_record(
        self, candidate: Optional[Dict[str, Any]], records: List[Dict[str, Any]]
    ) -> None:
        if not candidate:
            return
        hit = self._find_lap_record(candidate, records)
        if hit is None:
            records.append({"race_lap_record": candidate})
        else:
            i, existing = hit
            records[i]["race_lap_record"] = self.merge_lap_record(existing, candidate)
