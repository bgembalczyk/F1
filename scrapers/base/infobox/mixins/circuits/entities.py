from __future__ import annotations

import re
from typing import Optional, Dict, Any, List

from scrapers.base.infobox.mixins.circuits.geo import CircuitGeoMixin
from scrapers.base.infobox.mixins.circuits.history import CircuitHistoryMixin
from scrapers.base.infobox.mixins.circuits.specs import CircuitSpecsMixin


IGNORED_TOP_LEVEL_KEYS: set[str] = {
    # oryginalne labelki + wersje z małej litery na wszelki wypadek
    "Owner",
    "owner",
    "Operator",
    "operator",
    "Capacity",
    "capacity",
    "Construction cost",
    "construction cost",
    "Website",
    "website",
    "Area",
    "area",
    "Major events",
    "major events",
    "Address",
    "address",
}


class CircuitEntitiesMixin(
    CircuitGeoMixin, CircuitSpecsMixin, CircuitHistoryMixin
):
    """Łączy parsowanie linkowanych encji, lap recordów i buduje normalized/layouts."""

    # ------------------------------------
    # Pomocnicze do linków
    # ------------------------------------

    @staticmethod
    def _is_wikipedia_redlink(url: Optional[str]) -> bool:
        """Redlink typu ...w/index.php?title=...&action=edit&redlink=1."""
        if not url:
            return False
        url_l = url.lower()
        return (
            "wikipedia.org" in url_l
            and "action=edit" in url_l
            and "redlink=" in url_l
        )

    @staticmethod
    def _is_language_marker_link(text: str, url: Optional[str]) -> bool:
        """
        True dla markerów językowych typu:
        text='it', url='https://it.wikipedia.org/wiki/...'

        Warunki:
        - text = 1–3 litery,
        - URL do nieangielnej Wikipedii,
        - subdomena Wikipedii == text.
        """
        if not url:
            return False

        t = (text or "").strip().lower()
        if not re.fullmatch(r"[a-z]{1,3}", t):
            return False

        url_l = url.lower()
        m = re.search(r"://([a-z]{2,3})\.wikipedia\.org/", url_l)
        if not m:
            return False

        lang = m.group(1)
        if lang == "en":
            # en.wikipedia.org nie traktujemy jako marker językowy
            return False

        return lang == t

    # ------------------------------------
    # Encje typu Architect / Operator / Owner
    # ------------------------------------

    def _parse_linked_entity(
        self,
        row: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any] | str | List[Dict[str, Any]]]:
        if not row:
            return None

        text = self._get_text(row) or ""
        if not text:
            return None

        links = row.get("links") or []

        def _clean_link(link: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            link_text = (link.get("text") or "").strip()
            if not link_text:
                return None

            url = link.get("url")

            # 1) marker językowy [it], [fr] itp. → wywalamy cały wpis
            if self._is_language_marker_link(link_text, url):
                return None

            # 2) redlink → obcinamy URL, zostawiamy tylko tekst
            if self._is_wikipedia_redlink(url):
                url = None

            item: Dict[str, Any] = {"text": link_text}
            if url:
                item["url"] = url
            return item

        # Przypadek wielu linków – np. "Jarno Zaffelli [it]"
        if len(links) > 1:
            entities: List[Dict[str, Any]] = []
            for link in links:
                item = _clean_link(link)
                if item:
                    entities.append(item)
            return entities or None

        # pojedynczy link, ale tekst może mieć kilka części (A, B & C)
        parts = [p.strip() for p in re.split(r"\s*(?:,|&| and )\s*", text) if p.strip()]

        def _entity_for_part(part: str) -> Dict[str, Any]:
            # najpierw spróbuj dopasować link do konkretnej części tekstu
            link = self._find_link(part, links)
            if link:
                cleaned = _clean_link(link)
                if cleaned:
                    cleaned["text"] = part
                    return cleaned
            # jak nie ma linku / został odrzucony – zwróć sam tekst
            return {"text": part}

        if len(parts) > 1:
            return [_entity_for_part(p) for p in parts]

        # jeden link, jedna część tekstu
        if links:
            single = _clean_link(links[0])
            if single:
                # tekst z _get_text (bez [it])
                single["text"] = text
                return single

        # brak linków – zwracamy sam tekst
        return text or None

    # ------------------------------------
    # Website
    # ------------------------------------

    def _parse_website(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = self._get_text(row) or ""
        links = row.get("links") or []
        if links:
            return links[0].get("url") or text or None
        return text or None

    # ------------------------------------
    # Dodatkowe pola (additional_info)
    # ------------------------------------

    def _collect_additional_info(
        self, rows: Dict[str, Dict[str, Any]], used_keys: set[str]
    ) -> Optional[Dict[str, Any]]:
        additional: Dict[str, Any] = {}

        for key, row in rows.items():
            if key in used_keys:
                continue

            text = self._get_text(row)
            if not text:
                continue

            info: Dict[str, Any] = {"text": text}
            links = row.get("links") or []

            parts = [p.strip() for p in re.split(r";|,|/", text) if p.strip()]
            if len(parts) > 1:
                values: List[Any] = []
                for part in parts:
                    link = self._find_link(part, links)
                    if link and link.get("url"):
                        values.append({"text": part, "url": link.get("url")})
                    else:
                        values.append(part)
                info["values"] = values
            elif links:
                # tutaj nie czyścimy agresywnie – to tylko additional_info
                info["links"] = links

            additional[key] = info

        return additional or None

    # ------------------------------------
    # Lap record
    # ------------------------------------

    def _parse_lap_record(
        self, row: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        if not row:
            return None

        text = self._get_text(row) or ""
        if not text:
            return None

        time_match = re.search(r"\d+:\d{2}\.\d{3}", text)
        details_match = re.search(r"\(([^)]*)\)", text)

        details: List[str] = []
        if details_match:
            details = [
                part.strip()
                for part in details_match.group(1).split(",")
                if part.strip()
            ]

        record: Dict[str, Any] = {
            "time": time_match.group(0) if time_match else None,
        }

        if details:
            driver_text = details[0] if len(details) >= 1 else None
            car_text = details[1] if len(details) >= 2 else None
            links = row.get("links") or []

            def _link_for_entity(entity_text: str) -> Optional[str]:
                """Znajdź sensowny URL dla kierowcy/auta (o ile jest)."""
                # próbujemy dopasować pełny tekst
                link = self._find_link(entity_text, links)
                if not link and "/" in entity_text:
                    # dla "Mario Andretti / Denny Hulme" – spróbuj dopasować części
                    for part in [p.strip() for p in entity_text.split("/") if p.strip()]:
                        link = self._find_link(part, links)
                        if link:
                            break
                if not link:
                    return None
                url = link.get("url")
                if self._is_wikipedia_redlink(url):
                    return None
                return url

            def _wrap_entity(entity_text: Optional[str]) -> Optional[Dict[str, Any]]:
                if not entity_text:
                    return None
                url = _link_for_entity(entity_text)
                obj: Dict[str, Any] = {"text": entity_text}
                if url:
                    obj["url"] = url
                return obj

            record.update(
                {
                    "driver": _wrap_entity(driver_text),
                    "car": _wrap_entity(car_text),
                    "year": details[2] if len(details) >= 3 else None,
                    "series": details[3] if len(details) >= 4 else None,
                }
            )

        return record

    # ------------------------------------
    # Porównanie / merge lap records
    # ------------------------------------

    def _same_lap_record(
        self, left: Optional[Dict[str, Any]], right: Optional[Dict[str, Any]]
    ) -> bool:
        if not left or not right:
            return False

        def _text(obj: Optional[Dict[str, Any]]) -> Optional[str]:
            if not obj:
                return None
            return obj.get("text") if isinstance(obj, dict) else None

        return (
            left.get("time") == right.get("time")
            and _text(left.get("driver")) == _text(right.get("driver"))
            and _text(left.get("car")) == _text(right.get("car"))
            and left.get("year") == right.get("year")
            and left.get("series") == right.get("series")
        )

    def _lap_record_exists(
        self, candidate: Dict[str, Any], records: List[Dict[str, Any]]
    ) -> bool:
        for record in records:
            if self._same_lap_record(candidate, record.get("race_lap_record")):
                return True
        return False

    def _merge_records(
        self, base_record_row: Optional[Dict[str, Any]], layouts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []

        for layout in layouts:
            if layout.get("race_lap_record"):
                records.append(self._prune_nulls(layout))

        base_record = self._parse_lap_record(base_record_row)
        if base_record and not self._lap_record_exists(base_record, records):
            records.append({"race_lap_record": base_record})

        return records

    def _with_normalized(
        self,
        raw: Dict[str, Any],
        layout_records: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        rows: Dict[str, Dict[str, Any]] = raw.get("rows", {}) if raw else {}

        used_keys = {
            "Location",
            "Coordinates",
            "FIA Grade",
            "Length",
            "Turns",
            "Race lap record",
            "Opened",
            "Closed",
            "Former names",
            "Owner",
            "Operator",
            "Capacity",
            "Broke ground",
            "Built",
            "Construction cost",
            "Website",
            "Area",
            "Major events",
            "Address",
            "Architect",
            "Banking",
            "Surface",
        }

        normalized: Dict[str, Any] = {
            "name": raw.get("title"),
            "location": self._parse_location(rows.get("Location")),
            "coordinates": self._parse_coordinates(rows.get("Coordinates")),
            "specs": {
                "fia_grade": self._parse_int(rows.get("FIA Grade")),
                "length_km": self._parse_length(rows.get("Length"), unit="km"),
                "length_mi": self._parse_length(rows.get("Length"), unit="mi"),
                "turns": self._parse_int(rows.get("Turns")),
            },
            "history": self._parse_history(rows),
            "architect": self._parse_linked_entity(rows.get("Architect")),
        }

        extra_fields = self._collect_additional_info(rows, used_keys)
        if extra_fields:
            normalized["additional_info"] = extra_fields

        normalized = self._prune_nulls(normalized)

        # --- TU CZYŚCIMY RAW ---
        result: Dict[str, Any] = dict(raw or {})
        result.pop("rows", None)
        # wywal niechciane top-levelowe pola
        for key in IGNORED_TOP_LEVEL_KEYS:
            result.pop(key, None)

        layouts = layout_records or []
        if not layouts:
            default_layout: Dict[str, Any] = {
                "layout": None,
                "years": None,
                "length_km": normalized.get("specs", {}).get("length_km"),
                "length_mi": normalized.get("specs", {}).get("length_mi"),
                "turns": normalized.get("specs", {}).get("turns"),
                "race_lap_record": self._parse_lap_record(rows.get("Race lap record")),
                "surface": self._parse_surface(rows.get("Surface")),
                "banking": self._parse_banking(rows.get("Banking")),
            }
            default_layout = self._prune_nulls(default_layout)
            if default_layout:
                layouts = [default_layout]

        if layouts:
            result["layouts"] = self._prune_nulls(layouts)

        existing_norm = result.get("normalized")
        if isinstance(existing_norm, dict):
            existing_norm.update(normalized)
            result["normalized"] = existing_norm
        else:
            result["normalized"] = normalized

        return self._prune_nulls(result)
