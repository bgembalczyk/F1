from __future__ import annotations

import re
from typing import Optional, Dict, Any, List, Tuple

from scrapers.base.helpers.utils import (
    is_language_marker_link,
    is_wikipedia_redlink,
    split_delimited_text,
)
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


class CircuitEntitiesMixin(CircuitGeoMixin, CircuitSpecsMixin, CircuitHistoryMixin):
    """Łączy parsowanie linkowanych encji, lap recordów i buduje normalized/layouts."""

    # tylko markery językowe w nawiasie: (es), ( de ), (it)
    _LANG_PAREN_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)$", flags=re.IGNORECASE)
    _LANG_PAREN_ANYWHERE_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)", flags=re.IGNORECASE)

    # do czyszczenia uciętych markerów typu "( es" / "( cs"
    _LANG_PAREN_TAIL_RE = re.compile(r"\(\s*[a-z]{2,3}\s*\)?\s*$", flags=re.IGNORECASE)

    # do parsowania time -> seconds: "1:16.0357", "1:51.8", "38.891", "2:22.5"
    _TIME_PARSE_RE = re.compile(r"^\s*(?:(\d+):)?(\d{1,2})(?:\.(\d+))?\s*$")

    # ------------------------------------
    # Utils
    # ------------------------------------

    def _entity_text(self, val: Any) -> Optional[str]:
        if isinstance(val, dict):
            s = (val.get("text") or "").strip()
            return s or None
        if val is None:
            return None
        s = str(val).strip()
        return s or None

    def _entity_url(self, val: Any) -> Optional[str]:
        if isinstance(val, dict):
            return val.get("url") or None
        return None

    def _norm_time(self, t: Any) -> Optional[str]:
        """
        Normalizuje time do stringa (dla prezentacji).
        Uwaga: do porównań/scalania używamy _time_to_seconds.
        """
        if t is None:
            return None
        if isinstance(t, (int, float)):
            return f"{float(t):.6f}".rstrip("0").rstrip(".")
        s = str(t).strip()
        return s or None

    def _time_to_seconds(self, value: Any) -> Optional[float]:
        """
        Zamienia time (string lub number) na sekundy (float).
        Obsługuje:
        - "M:SS"
        - "M:SS.d", "M:SS.dd", "M:SS.ddd", "M:SS.dddd"...
        - "SS.ddd" itp.
        """
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)

        s = str(value).strip()
        m = self._TIME_PARSE_RE.match(s)
        if not m:
            return None

        mm = m.group(1)
        ss = m.group(2)
        frac = m.group(3) or "0"

        minutes = int(mm) if mm is not None else 0
        seconds = int(ss)
        frac_seconds = int(frac) / (10 ** len(frac)) if frac else 0.0
        return minutes * 60.0 + seconds + frac_seconds

    def _get_vehicle_field(self, rec: Dict[str, Any]) -> Any:
        return rec.get("vehicle") or rec.get("car")

    def _get_class_field(self, rec: Dict[str, Any]) -> Any:
        # traktujemy category/class/series jako to samo semantycznie
        return rec.get("series") or rec.get("category") or rec.get("class")

    def _strip_lang_markers(self, s: str) -> str:
        """
        Usuwa tylko śmieciowe markery językowe:
        - '(es)' '( de )' '(it)' itp. (również w środku tekstu, gdy psują parsing)
        Nie dotyka normalnych nawiasów: '(motorcyclist)'.
        """
        s = (s or "").replace("\xa0", " ").strip()
        s = self._LANG_PAREN_ANYWHERE_RE.sub("", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _strip_lang_marker_tail_only(self, s: str) -> str:
        """
        Usuwa ucięte markery na końcu:
        - "Juan Martín Trucco ( es" -> "Juan Martín Trucco"
        - "David Vršecký ( cs" -> "David Vršecký"
        """
        s = (s or "").replace("\xa0", " ").strip()
        s = self._LANG_PAREN_TAIL_RE.sub("", s).strip()
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _norm_text_for_key(self, x: Any) -> str:
        if isinstance(x, dict):
            x = x.get("text") or ""
        return self._strip_lang_marker_tail_only(str(x or "")).strip().lower()

    def _extract_outer_parens(self, text: str) -> Optional[str]:
        """
        Zwraca zawartość pierwszego zewnętrznego nawiasu (...) z uwzględnieniem
        zagnieżdżeń w środku.
        """
        if not text:
            return None
        start = text.find("(")
        if start < 0:
            return None

        depth = 0
        inner_start: Optional[int] = None

        for i in range(start, len(text)):
            ch = text[i]
            if ch == "(":
                depth += 1
                if depth == 1:
                    inner_start = i + 1
            elif ch == ")":
                if depth == 1 and inner_start is not None:
                    return text[inner_start:i]
                depth = max(depth - 1, 0)

        return None

    def _is_en_wiki(self, url: Optional[str]) -> bool:
        if not url:
            return False
        return url.startswith("https://en.wikipedia.org/") or url.startswith("http://en.wikipedia.org/")

    def _choose_richer_entity(self, a: Any, b: Any) -> Any:
        """
        Preferuj encję z url; jeśli oba mają url albo oba nie mają,
        wybierz tę z dłuższym textem.
        """
        if not a:
            return b
        if not b:
            return a

        # preferuj dicta nad stringi
        if isinstance(a, dict) and not isinstance(b, dict):
            return a
        if isinstance(b, dict) and not isinstance(a, dict):
            return b

        a_url = self._entity_url(a)
        b_url = self._entity_url(b)
        if a_url and not b_url:
            return a
        if b_url and not a_url:
            return b

        a_txt = self._entity_text(a) or ""
        b_txt = self._entity_text(b) or ""
        return a if len(a_txt) >= len(b_txt) else b

    # ------------------------------------
    # Encje typu Architect / Operator / Owner
    # ------------------------------------

    def _parse_linked_entity(
        self,
        row: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any] | str | List[Dict[str, Any]]]:
        if not row:
            return None

        text = (self._get_text(row) or "").strip()
        if not text:
            return None

        links = row.get("links") or []

        def _clean_link(link: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            link_text = (link.get("text") or "").strip()
            if not link_text:
                return None

            url = link.get("url")

            # marker językowy typu "it" + https://it.wikipedia.org/... -> OUT
            if is_language_marker_link(link_text, url):
                return None

            # redlink -> url None, zostaw tekst
            if is_wikipedia_redlink(url):
                url = None

            item: Dict[str, Any] = {"text": link_text}
            if url:
                item["url"] = url
            return item

        # wiele linków -> lista (pomijamy językowe)
        if len(links) > 1:
            out: List[Dict[str, Any]] = []
            for link in links:
                item = _clean_link(link)
                if item:
                    out.append(item)
            return out or self._strip_lang_markers(text) or None

        # pojedynczy link, ale tekst bywa "A, B and C"
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
        text = (self._get_text(row) or "").strip()
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

            text = (self._get_text(row) or "").strip()
            if not text:
                continue

            info: Dict[str, Any] = {"text": text}
            links = row.get("links") or []

            parts = split_delimited_text(text)
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
    # Lap record parsing
    # ------------------------------------

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

    # ------------------------------------
    # Lap record merge (infobox vs tabela)
    # ------------------------------------

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

    # ------------------------------------
    # Normalized/layouts
    # ------------------------------------

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

        # --- RAW cleanup ---
        result: Dict[str, Any] = dict(raw or {})
        result.pop("rows", None)
        for key in IGNORED_TOP_LEVEL_KEYS:
            result.pop(key, None)

        # --- Layouts ---
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

        # jeśli są layouty, to dopilnuj że lap record z infoboxa nie zdubluje rekordów z layout_records
        if layouts:
            base_record = self._parse_lap_record(rows.get("Race lap record"))
            if base_record:
                matched = False

                # 1) spróbuj dopasować do istniejącego layoutu i zmergować
                for lay in layouts:
                    existing = lay.get("race_lap_record")
                    if not existing:
                        continue

                    if self._same_lap_record(base_record, existing):
                        lay["race_lap_record"] = self._merge_lap_record(existing, base_record)
                        matched = True
                        break

                # 2) jeśli nie ma dopasowania:
                if not matched:
                    # jeśli jest dokładnie jeden layout i nie ma rekordu – podepnij go tam
                    if len(layouts) == 1 and not layouts[0].get("race_lap_record"):
                        layouts[0]["race_lap_record"] = base_record
                    else:
                        # w innym wypadku dodaj dodatkowy "layout" tylko dla tego rekordu
                        layouts.append(
                            self._prune_nulls(
                                {
                                    "layout": None,
                                    "years": None,
                                    "race_lap_record": base_record,
                                }
                            )
                        )

            result["layouts"] = self._prune_nulls(layouts)

        existing_norm = result.get("normalized")
        if isinstance(existing_norm, dict):
            existing_norm.update(normalized)
            result["normalized"] = existing_norm
        else:
            result["normalized"] = normalized

        return self._prune_nulls(result)
