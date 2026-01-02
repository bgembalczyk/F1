import re
from typing import Any, Dict, List, Optional, Tuple

from models.records.link import LinkRecord
from models.services.circuits.lap_record_utils import (
    build_lap_record_key,
    extract_year,
    normalize_lap_record_entity,
)
from models.services.circuits.lap_record_merging import (
    merge_two_records,
    normalize_lap_record,
)
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.time import parse_time_seconds_from_text
from scrapers.base.helpers.wiki import is_wikipedia_redlink
from scrapers.circuits.helpers.lap_record import extract_time
from scrapers.circuits.helpers.lap_record import select_details_paren
from scrapers.circuits.infobox.services.text_processing import CircuitTextProcessing


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

        text = clean_infobox_text(row.get("text")) or ""
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

    def _lap_record_key(
        self, rec: Dict[str, Any]
    ) -> Optional[Tuple[str, str, str, float]]:
        """
        Buduje klucz do identyfikacji tego samego lap record.
        Klucz: (driver, vehicle, year, time)
        """
        sanitizer = self._strip_lang_marker_tail_only
        return build_lap_record_key(
            rec,
            year_extractor=lambda r: extract_year(r),
            vehicle_getter=lambda r: self._get_vehicle_field(r),
            driver_normalizer=lambda value: normalize_lap_record_entity(
                value, sanitizer=sanitizer
            ),
            vehicle_normalizer=lambda value: normalize_lap_record_entity(
                value, sanitizer=sanitizer
            ),
        )

    def same_lap_record(self, left: dict, right: dict) -> bool:
        if not left or not right:
            return False
        kl = self._lap_record_key(left)
        kr = self._lap_record_key(right)
        return bool(kl and kr and kl == kr)

    def _upsert_lap_record(
        self, candidate: Optional[Dict[str, Any]], records: List[Dict[str, Any]]
    ) -> None:
        if not candidate:
            return

        cand_key = self._lap_record_key(candidate)
        if cand_key is None:
            records.append({"race_lap_record": candidate})
            return

        for i, record in enumerate(records):
            existing = record.get("race_lap_record")
            if not existing:
                continue
            if self._lap_record_key(existing) == cand_key:
                normalize_lap_record(existing)
                normalize_lap_record(candidate)
                merged = merge_two_records(existing, candidate)
                records[i]["race_lap_record"] = self.prune_nulls(merged)
                return

        records.append({"race_lap_record": candidate})
