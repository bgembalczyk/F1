from __future__ import annotations

from typing import Any, Dict, List, Optional
import re


def _add_name(names_set: set[str], name_list: List[str], value: Optional[str]) -> None:
    if not value:
        return
    value = value.strip()
    if value and value not in names_set:
        names_set.add(value)
        name_list.append(value)


def _safe_text(obj: Any) -> str:
    if isinstance(obj, dict):
        return (obj.get("text") or "").strip().lower()
    if obj is None:
        return ""
    return str(obj).strip().lower()


def _time_key(rec: Dict[str, Any]) -> Optional[float | str]:
    """
    Normalizuje time do postaci klucza:
    - jeśli mamy seconds -> używamy seconds (float)
    - jeśli mamy tekst, próbujemy sparsować MM:SS.xxx -> sekundy
    - jak się nie uda, używamy znormalizowanego tekstu
    """
    t = rec.get("time")

    # jeśli to już liczba (po naszym cleanupie), użyj bezpośrednio
    if isinstance(t, (int, float)):
        return float(t)

    txt: Optional[str] = None

    if isinstance(t, dict):
        if "seconds" in t and isinstance(t["seconds"], (int, float)):
            return float(t["seconds"])
        txt = t.get("text")
    elif t is not None:
        txt = str(t)

    if not txt:
        return None

    s = txt.strip()

    # spróbuj sparsować MM:SS.xxx
    m = re.match(r"(?:(\d+):)?(\d+(?:\.\d+)?)", s)
    if m:
        minutes = int(m.group(1)) if m.group(1) else 0
        seconds = float(m.group(2))
        return minutes * 60 + seconds

    # fallback – traktujemy jako tekstowy klucz
    return s.lower()


def _record_key(rec: Dict[str, Any]) -> Optional[tuple]:
    """
    Klucz do rozpoznawania tego samego rekordu:

    (driver_text, vehicle_text, year, time_key)

    - driver: rec["driver"]["text"] / rec["driver"]
    - vehicle: rec["vehicle"]["text"] / rec["car"]["text"]
    - year: rec["year"] albo rok z rec["date"]["iso"]
    - time: seconds lub sparsowany MM:SS.xxx

    UWAGA: series/category/class NIE jest częścią klucza – jeśli
    wszystko powyższe się zgadza, a różni się tylko series/category,
    traktujemy rekordy jako ten sam lap record.
    """
    driver_txt = _safe_text(rec.get("driver"))

    vehicle_obj = rec.get("vehicle")
    if vehicle_obj is None:
        vehicle_obj = rec.get("car")
    vehicle_txt = _safe_text(vehicle_obj)

    # year z pola year lub z date.iso
    year: Optional[str] = None
    if "year" in rec and rec["year"] is not None:
        year = str(rec["year"])
    else:
        date_obj = rec.get("date")
        if isinstance(date_obj, dict):
            iso = (date_obj.get("iso") or "").strip()
            if iso:
                year = iso[:4]

    time_key = _time_key(rec)

    if not driver_txt or not vehicle_txt or not year or time_key is None:
        return None

    return (driver_txt, vehicle_txt, year, time_key)


def _merge_race_lap_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Łączy duplikujące się rekordy (infobox + tabela) w jeden bogaty rekord.
    """
    result: List[Dict[str, Any]] = []
    processed_keys: set[tuple] = set()

    for rec in records:
        key = _record_key(rec)
        if key is None:
            # nie umiemy dobrze dopasować – zostawiamy jak jest
            result.append(rec)
            continue

        if key in processed_keys:
            continue

        # zbierz wszystkie rekordy z tym samym kluczem
        same: List[Dict[str, Any]] = [
            r for r in records if _record_key(r) == key
        ]

        merged = _merge_record_group(same)
        result.append(merged)
        processed_keys.add(key)

    return result


def _merge_record_group(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Scala grupę rekordów opisujących ten sam lap record.

    Reguły:
    - time: preferujemy wersję z 'seconds'
    - date: preferujemy dokładniejszą iso (dłuższy string)
    - series/category/class: wynikowo pole 'series' (preferujemy wersję z linkiem)
    - vehicle/car: wynikowo 'vehicle' (preferujemy wersję z linkiem)
    - driver: preferujemy wersję z linkiem
    - inne pola: bierzemy pierwszy niepusty
    """
    merged: Dict[str, Any] = {}

    # 1) driver
    best_driver = None
    for r in records:
        d = r.get("driver")
        if not d:
            continue
        if best_driver is None:
            best_driver = d
            continue
        # preferuj driver jako dict z URL
        if isinstance(d, dict) and d.get("url") and (
            not isinstance(best_driver, dict) or not best_driver.get("url")
        ):
            best_driver = d

    # 2) vehicle / car -> vehicle
    best_vehicle = None
    for r in records:
        v = r.get("vehicle")
        if v is None:
            v = r.get("car")
        if not v:
            continue
        if best_vehicle is None:
            best_vehicle = v
            continue
        # preferuj wersję z linkiem
        if isinstance(v, dict) and v.get("url") and (
            not isinstance(best_vehicle, dict) or not best_vehicle.get("url")
        ):
            best_vehicle = v

    # 3) time
    def has_seconds(val: Any) -> bool:
        return isinstance(val, dict) and "seconds" in val

    best_time = None
    for r in records:
        t = r.get("time")
        if not t:
            continue
        if best_time is None:
            best_time = t
            continue
        if has_seconds(t) and not has_seconds(best_time):
            best_time = t

    # 4) date + year
    best_date = None
    best_year = None

    for r in records:
        # year
        if best_year is None and r.get("year") is not None:
            best_year = r.get("year")

        # date
        d = r.get("date")
        if not d:
            continue
        if best_date is None:
            best_date = d
            continue

        iso_cur = (best_date.get("iso") if isinstance(best_date, dict) else "") or ""
        iso_new = (d.get("iso") if isinstance(d, dict) else "") or ""
        # preferuj dłuższy iso (YYYY-MM-DD > YYYY-MM > YYYY)
        if len(iso_new) > len(iso_cur):
            best_date = d

    # 5) series / category / class -> series
    def series_candidate(r: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cand = (
            r.get("series")
            or r.get("category")
            or r.get("class")
            or r.get("class_")
        )
        if cand is None:
            return None
        if isinstance(cand, dict):
            return {
                "text": cand.get("text") or cand.get("name") or "",
                "url": cand.get("url"),
            }
        # zwykły tekst
        return {"text": str(cand), "url": None}

    best_series = None
    best_series_has_url = False
    best_series_len = 0

    for r in records:
        cand = series_candidate(r)
        if not cand:
            continue

        text = (cand.get("text") or "").strip()
        has_url = bool(cand.get("url"))
        text_len = len(text)

        if best_series is None:
            # pierwszy kandydat
            best_series = cand
            best_series_has_url = has_url
            best_series_len = text_len
            continue

        # jeśli ten ma URL, a dotychczasowy nie – bierzemy ten
        if has_url and not best_series_has_url:
            best_series = cand
            best_series_has_url = True
            best_series_len = text_len
            continue

        # jeśli oba mają (albo oba nie mają) URL – wybieramy dłuższą nazwę
        if has_url == best_series_has_url and text_len > best_series_len:
            best_series = cand
            best_series_len = text_len

    # 6) inne pola – pierwszy niepusty
    ignore_keys = {
        "driver",
        "vehicle",
        "car",
        "time",
        "date",
        "year",
        "series",
        "category",
        "class",
        "class_",
    }

    for r in records:
        for k, v in r.items():
            if k in ignore_keys:
                continue
            if k not in merged and v is not None:
                merged[k] = v

    if best_driver is not None:
        merged["driver"] = best_driver
    if best_vehicle is not None:
        merged["vehicle"] = best_vehicle
    if best_time is not None:
        merged["time"] = best_time
    if best_date is not None:
        merged["date"] = best_date
    elif best_year is not None:
        merged["year"] = best_year
    if best_series is not None:
        merged["series"] = best_series

    return merged


def normalize_circuit_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizuje pojedynczy rekord toru wg ustalonych zasad:

    - circuit[text] -> name.list (dodajemy też infobox.title i infobox.normalized.name)
    - circuit[url] -> url, ale jeśli details == None -> url = None
    - former_names -> name.former_names
    - layouts z infobox.layouts przenosimy na górę, race_lap_record -> race_lap_records (lista)
    - tables łączymy z layouts (lap_records -> race_lap_records odpowiedniego layoutu)
    - location: { places, coordinates }
    - fia_grade wyciągnięte na wierzch
    - history: tylko lista events
    - nie kopiujemy last_length_used_km, last_length_used_mi, turns, specs (poza fia_grade)
    """
    out: Dict[str, Any] = {}

    circuit = raw.get("circuit") or {}
    details = raw.get("details")

    # -----------------------
    # name + url
    # -----------------------
    name_set: set[str] = set()
    name_list: List[str] = []

    # 1) circuit[text] -> name.list
    _add_name(name_set, name_list, circuit.get("text"))

    infobox = None
    normalized = None
    if isinstance(details, dict):
        infobox = (details or {}).get("infobox") or {}
        normalized = infobox.get("normalized") or {}

    # 2) infobox.title + infobox.normalized.name
    if infobox:
        _add_name(name_set, name_list, infobox.get("title"))
    if normalized:
        _add_name(name_set, name_list, normalized.get("name"))

    # 3) former_names -> name.former_names
    former_names: List[Dict[str, Any]] = []
    if normalized:
        history_norm = normalized.get("history") or {}
        former_names = history_norm.get("former_names") or []

    out["name"] = {
        "list": name_list,
        "former_names": former_names,
    }

    # url:
    # - jeśli details jest None -> url = None
    # - w pozostałych przypadkach bierzemy circuit["url"]
    if details is None:
        out["url"] = None
    else:
        out["url"] = circuit.get("url")

    # -----------------------
    # proste pola z wierzchu
    # -----------------------
    for key in (
        "circuit_status",
        "type",
        "direction",
        "grands_prix",
        "seasons",
        "grands_prix_held",
    ):
        if key in raw:
            out[key] = raw[key]

    # -----------------------
    # location -> nowa struktura:
    #   {
    #       "places": [ {text, url}, ... ],
    #       "coordinates": {...}
    #   }
    #
    # places = unikalne miejsca z:
    #   - old_location
    #   - new_location (infobox.normalized.location)
    #   - country (dodawany jako miejsce)
    # -----------------------

    country = raw.get("country")
    old_location = raw.get("location")  # np. {"text": "Adelaide", "url": "..."}
    new_location = None
    coordinates = None

    if normalized:
        new_location = normalized.get("location")
        coordinates = normalized.get("coordinates")

    def extract_place(
        text: Optional[str], url: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        clean = text.strip()
        if not clean:
            return None
        return {"text": clean, "url": url}

    # ordered-set by place text
    places_map: Dict[str, Dict[str, Any]] = {}

    # 1) old_location → places
    if isinstance(old_location, dict):
        p = extract_place(old_location.get("text"), old_location.get("url"))
        if p:
            places_map[p["text"]] = p

    # 2) new_location → places
    if isinstance(new_location, dict):
        for _, val in new_location.items():
            if not isinstance(val, dict):
                continue

            text = val.get("text") or val.get("label")
            link = val.get("link") or {}
            url = link.get("url")

            p = extract_place(text, url)
            if p:
                places_map[p["text"]] = p

    # 3) country też trafia do places
    if country:
        p = extract_place(country, None)
        if p:
            places_map.setdefault(p["text"], p)

    out["location"] = {
        "places": list(places_map.values()),
        "coordinates": coordinates,
    }

    # -----------------------
    # fia_grade + history (events)
    # -----------------------
    fia_grade = None
    history_events = None

    if normalized:
        specs = normalized.get("specs") or {}
        fia_grade = specs.get("fia_grade")
        history_norm = normalized.get("history") or {}
        history_events = history_norm.get("events") or None

    if fia_grade is not None:
        out["fia_grade"] = fia_grade

    if history_events is not None:
        out["history"] = history_events

    # -----------------------
    # layouts (z infoboxa)
    #   - przenosimy na górę
    #   - race_lap_record -> race_lap_records (lista)
    # -----------------------
    layouts: List[Dict[str, Any]] = []
    if infobox:
        for layout in infobox.get("layouts") or []:
            lay = dict(layout)
            rlr = lay.pop("race_lap_record", None)
            records: List[Dict[str, Any]] = []
            if rlr is not None:
                records.append(rlr)
            lay["race_lap_records"] = records
            layouts.append(lay)

    # -----------------------
    # tables łączymy z layouts
    # -----------------------
    tables = None
    if isinstance(details, dict):
        tables = details.get("tables")
    tables = tables or []

    def find_layout_for_table(table_layout: str) -> Optional[Dict[str, Any]]:
        """
        Dopasowuje layout z tabeli do layoutu z infoboxa na podstawie:
        - długości okrążenia (km),
        - lat obowiązywania layoutu.

        Format z tabeli jest zwykle typu:
        "Supercars Circuit: 3.219 km (1999–present)"
        """
        if not table_layout:
            return None

        # --- parsujemy informacje z tekstu layoutu z tabeli ---
        length_km: Optional[float] = None
        years_str: Optional[str] = None

        # długość w km
        m_len = re.search(r"([\d.,]+)\s*km", table_layout)
        if m_len:
            length_km = float(m_len.group(1).replace(",", "."))

        # lata w nawiasie na końcu
        m_years = re.search(r"\(([^()]*)\)\s*$", table_layout)
        if m_years:
            years_str = m_years.group(1).strip().lower()

        best_candidate: Optional[Dict[str, Any]] = None

        for lay in layouts:
            lay_len = lay.get("length_km")
            lay_years_raw = lay.get("years") or ""
            lay_years = lay_years_raw.strip().lower()

            # 1) dopasowanie długości
            if length_km is not None and lay_len is not None:
                if abs(lay_len - length_km) > 1e-3:
                    # inne okrążenie – odrzucamy
                    continue

            # 2) dopasowanie lat
            if years_str and lay_years:
                # idealny przypadek – dokładnie ten sam string (po normalizacji)
                if years_str == lay_years:
                    return lay

                # bardziej miękka heurystyka:
                # porównujemy rok startowy (pierwszy rok w stringu)
                y_tab = re.search(r"\d{4}", years_str)
                y_lay = re.search(r"\d{4}", lay_years)
                if y_tab and y_lay and y_tab.group(0) != y_lay.group(0):
                    # inne lata startu – odrzucamy
                    continue

            # jeżeli przeszliśmy powyższe filtry – traktujemy jako kandydata
            if best_candidate is None:
                best_candidate = lay

        return best_candidate

    for table_block in tables:
        t_layout_str = table_block.get("layout")
        lap_records = table_block.get("lap_records") or []
        if not t_layout_str:
            continue

        target_layout = find_layout_for_table(t_layout_str)
        if target_layout is None:
            # nie ma takiego layoutu – dodajemy nowy
            layouts.append(
                {
                    "layout": t_layout_str,
                    "race_lap_records": list(lap_records),
                }
            )
        else:
            target_layout.setdefault("race_lap_records", [])
            target_layout["race_lap_records"].extend(lap_records)

    # --- deduplikacja i scalanie race_lap_records w ramach każdego layoutu ---
    for lay in layouts:
        records = lay.get("race_lap_records") or []
        if records:
            lay["race_lap_records"] = _merge_race_lap_records(records)

    if layouts:
        out["layouts"] = layouts

    # -----------------------
    # FINAL CLEANUP JSON
    # -----------------------

    def cleanup_urls(obj: Any) -> Any:
        """
        Usuwa url=None oraz rekursywnie czyści elementy.
        """
        if isinstance(obj, list):
            return [cleanup_urls(x) for x in obj if x is not None]

        if isinstance(obj, dict):
            cleaned = {}
            for k, v in obj.items():
                if v is None:
                    continue
                cv = cleanup_urls(v)
                # pomiń puste listy
                if cv == []:
                    continue
                # pomiń dict zawierający tylko url:null
                if isinstance(cv, dict) and set(cv.keys()) == set():
                    continue
                cleaned[k] = cv
            return cleaned

        return obj

    def simplify_time(rec: Dict[str, Any]) -> None:
        """
        Zamienia time dict na float jeśli jest seconds,
        albo próbuje zparsować tekstowo.
        """
        t = rec.get("time")
        if not isinstance(t, dict):
            return

        # preferuj seconds
        if "seconds" in t:
            rec["time"] = t["seconds"]
            return

        # fallback: spróbuj sparsować t["text"]
        txt = t.get("text")
        if not txt:
            rec["time"] = None
            return

        # parse MM:SS.xxx
        import re
        m = re.match(r"(?:(\d+):)?(\d+\.\d+|\d+)", txt.strip())
        if m:
            minutes = int(m.group(1)) if m.group(1) else 0
            seconds = float(m.group(2))
            rec["time"] = minutes * 60 + seconds
        else:
            # jeśli się nie da — zostaw tekst
            rec["time"] = txt

    def simplify_date(rec: Dict[str, Any]) -> None:
        """
        Zamienia date dict na wartość "YYYY-MM-DD" lub "YYYY-MM" lub "YYYY".
        """
        d = rec.get("date")
        if not isinstance(d, dict):
            return
        iso = d.get("iso")
        if iso:
            rec["date"] = iso
        else:
            # fallback — jeśli był tylko rok
            txt = d.get("text")
            if txt:
                rec["date"] = txt.strip()

    # -----------------------
    # APPLY CLEANUP TO LAYOUT RECORDS
    # -----------------------

    for lay in out.get("layouts", []):
        records = lay.get("race_lap_records", [])
        for r in records:
            simplify_time(r)
            simplify_date(r)

    # -----------------------
    # CLEAN URL=NULL IN WHOLE OUTPUT
    # -----------------------

    out = cleanup_urls(out)

    # -----------------------
    # REMOVE EMPTY LISTS (e.g. former_names: [])
    # -----------------------

    def remove_empty_lists(obj):
        if isinstance(obj, dict):
            keys_to_del = []
            for k, v in obj.items():
                rv = remove_empty_lists(v)
                if rv == []:
                    keys_to_del.append(k)
                else:
                    obj[k] = rv
            for k in keys_to_del:
                del obj[k]
            return obj
        if isinstance(obj, list):
            new_list = [remove_empty_lists(x) for x in obj]
            return [x for x in new_list if x != []]
        return obj

    out = remove_empty_lists(out)

    return out

