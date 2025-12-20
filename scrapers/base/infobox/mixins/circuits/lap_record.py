# scrapers/base/infobox/mixins/circuits/lap_record.py

import re
from typing import Any, Dict, List, Optional, Tuple

from scrapers.base.helpers.utils import is_wikipedia_redlink
from scrapers.base.infobox.mixins.circuits.additional_info import CircuitAdditionalInfoMixin


class CircuitLapRecordMixin(CircuitAdditionalInfoMixin):
    """Logika parsowania, porównywania i scalania lap record'ów."""

    def _wrap_entity_from_links(
        self, entity_text: Optional[str], links: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        if not entity_text:
            return None

        cleaned = self._strip_lang_markers(entity_text).strip()
        cleaned = self._strip_lang_marker_tail_only(cleaned).strip()
        if not cleaned:
            return None

        obj: Dict[str, Any] = {"text": cleaned}

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

    def _parse_lap_record(self, row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Parsuje pojedynczą komórkę "Race lap record" z infoboksa.

        Zwraca rekord w formacie:
        {
          "time": <float sekundy>,
          "driver": {text,url}?,
          "vehicle": {text,url}?,
          "year": "2023"?,
          "series": {text,url}?      # semantycznie: series/category/class
        }
        """
        if not row:
            return None

        text = self._get_text(row) or ""
        if not text:
            return None

        links = row.get("links") or []

        # 1) czas zwykle stoi na początku, przed nawiasem
        head = text.split("(", 1)[0].strip()
        time_match = re.match(r"^\s*(\d+:\d{2}(?:\.\d+)?)\b", head)
        time_str = time_match.group(1) if time_match else None

        sec: Optional[float] = self._time_to_seconds(time_str) if time_str else None

        # fallback: czas gdziekolwiek w tekście (rzadkie)
        if sec is None:
            m = re.search(r"\b(\d+:\d{2}(?:\.\d+)?)\b", text)
            if m:
                sec = self._time_to_seconds(m.group(1))

        record: Dict[str, Any] = {}
        if sec is not None:
            record["time"] = sec

        # 2) detale w nawiasie: driver, car, year, series
        details_match = re.search(r"\(([^)]*)\)", text)
        details: List[str] = []
        if details_match:
            details = [p.strip() for p in details_match.group(1).split(",") if p.strip()]

        if not details:
            return self._prune_nulls(record) or None

        driver_text = details[0] if len(details) >= 1 else None
        car_text = details[1] if len(details) >= 2 else None
        year_text = details[2] if len(details) >= 3 else None
        series_text = details[3] if len(details) >= 4 else None

        record.update(
            {
                "driver": self._wrap_entity_from_links(driver_text, links),
                "vehicle": self._wrap_entity_from_links(car_text, links),
                "year": year_text,
                "series": self._wrap_entity_from_links(series_text, links) if series_text else None,
            }
        )

        return self._prune_nulls(record) or None

    def _year_from_record(self, rec: Dict[str, Any]) -> Optional[str]:
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

    def _lap_record_key(self, rec: Dict[str, Any]) -> Optional[Tuple[str, str, int, str]]:
        """
        Klucz porównania IGNORUJE różnice series/category/class.
        Porównuje:
        - driver.text (znormalizowany + czyszczenie "( es" / "( cs")
        - vehicle/car (znormalizowany)
        - time w sekundach (ms) -> żeby 1:16.0357 == 76.0357
        - rok (year lub z date/event)
        """
        driver = rec.get("driver")
        vehicle = self._get_vehicle_field(rec)

        d = self._norm_text_for_key(driver)
        v = self._norm_text_for_key(vehicle)
        if not d or not v:
            return None

        sec = self._time_to_seconds(rec.get("time"))
        if sec is None:
            return None

        year = self._year_from_record(rec)
        if not year:
            return None

        return (d, v, int(round(sec * 1000)), year)

    def _merge_two_lap_records(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Łączy dwa rekordy w jeden "bogatszy".
        Normalizuje wynik:
        - vehicle jako pole główne (usuwa car),
        - series jako pole główne (usuwa category/class),
        - time: zawsze float w sekundach (bez time_seconds i bez stringów).
        """
        out = dict(a)

        # driver
        out["driver"] = self._choose_richer_entity(a.get("driver"), b.get("driver"))

        # vehicle/car -> vehicle
        out["vehicle"] = self._choose_richer_entity(
            self._get_vehicle_field(a), self._get_vehicle_field(b)
        )
        out.pop("car", None)

        # series/category/class -> series (bogatszy)
        picked_series = self._choose_richer_entity(self._get_class_field(a), self._get_class_field(b))
        if picked_series:
            out["series"] = picked_series
        out.pop("category", None)
        out.pop("class", None)

        # proste pola: doklej brakujące
        for k in ("event", "date", "year", "source", "notes"):
            if not out.get(k) and b.get(k):
                out[k] = b[k]

        # time: zawsze sekundy (float)
        a_sec = self._time_to_seconds(a.get("time"))
        b_sec = self._time_to_seconds(b.get("time"))
        sec = a_sec if a_sec is not None else b_sec
        if sec is not None:
            out["time"] = sec
        else:
            out.pop("time", None)

        # posprzątaj ewentualne stare pola
        out.pop("time_seconds", None)

        # year: jeśli brak, spróbuj wydedukować (np. z date/event)
        out["year"] = out.get("year") or self._year_from_record(out)

        return self._prune_nulls(out)

    def _same_lap_record(self, left: dict, right: dict) -> bool:
        """
        Nowa definicja "to ten sam rekord":
        - ignorujemy series/category/class
        - normalizujemy driver/vehicle
        - porównujemy time w ms
        - porównujemy rok (year lub z date/event)
        """
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

    def _merge_lap_record(self, existing: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
        return self._merge_two_lap_records(existing, candidate)

    def _upsert_lap_record(self, candidate: Optional[Dict[str, Any]], records: List[Dict[str, Any]]) -> None:
        if not candidate:
            return
        hit = self._find_lap_record(candidate, records)
        if hit is None:
            records.append({"race_lap_record": candidate})
        else:
            i, existing = hit
            records[i]["race_lap_record"] = self._merge_lap_record(existing, candidate)

