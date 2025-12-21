from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import re


_YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")


def _norm_driver_text(obj: Any) -> str:
    s = _safe_text(obj)
    if not s:
        return ""
    # usuń dopiski w nawiasach: "hailey (tum)" -> "hailey"
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s)
    s = " ".join(s.split())
    return s

def _driver_loose_match(a: Any, b: Any, *, min_len: int = 4) -> bool:
    da = _norm_driver_text(a)
    db = _norm_driver_text(b)
    if not da or not db:
        return False
    if len(da) < min_len or len(db) < min_len:
        return False
    return da == db or da.startswith(db) or db.startswith(da) or (da in db) or (db in da)

def _is_subset_record(small: Dict[str, Any], big: Dict[str, Any]) -> bool:
    """
    True, jeśli small nie wnosi sprzecznych danych względem big.
    Używamy tylko do bezpiecznego fallback-merge.
    """
    # porównujemy tylko klucze, które są w small
    for k, sv in small.items():
        if sv is None:
            continue
        if k not in big or big.get(k) is None:
            continue

        bv = big.get(k)

        # time porównujemy jako sekundy
        if k == "time":
            st = _time_seconds({"time": sv} if not isinstance(sv, dict) else {"time": sv})
            bt = _time_seconds({"time": bv} if not isinstance(bv, dict) else {"time": bv})
            if st is None or bt is None:
                continue
            if round(float(st), 6) != round(float(bt), 6):
                return False
            continue

        # driver/vehicle porównujemy po tekście (luźno)
        if k == "driver":
            if not _driver_loose_match(sv, bv):
                return False
            continue
        if k in ("vehicle", "car"):
            # jeśli small ma vehicle, a big też, to prefix match OK
            if not _vehicle_prefix_match(sv, bv, min_len=6):
                return False
            continue

        # dicty: porównuj po "text" jeśli jest
        if isinstance(sv, dict) and isinstance(bv, dict):
            stxt = (sv.get("text") or sv.get("name") or "").strip().lower()
            btxt = (bv.get("text") or bv.get("name") or "").strip().lower()
            if stxt and btxt and stxt != btxt:
                return False
            continue

        # fallback: proste porównanie
        if sv != bv:
            return False

    return True

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

def _extract_year_from_event(rec: Dict[str, Any]) -> Optional[str]:
    """
    Fallback dla rekordów tabelarycznych, które nie mają `year` ani `date`,
    ale mają `event` (np. "1963 Aintree 200", url: ".../1963_Aintree_200").
    """
    event = rec.get("event")
    candidates: List[str] = []

    if isinstance(event, dict):
        if event.get("text"):
            candidates.append(str(event["text"]))
        if event.get("url"):
            candidates.append(str(event["url"]))
    elif isinstance(event, str):
        candidates.append(event)

    for s in candidates:
        m = _YEAR_RE.search(s)
        if m:
            return m.group(1)

    return None

def _time_seconds(rec: Dict[str, Any]) -> Optional[float]:
    """
    Zwraca czas WYŁĄCZNIE jako sekundy (float) albo None.
    Obsługuje:
    - rec["time_seconds"] (jeśli istnieje)
    - rec["time"] jako liczba
    - rec["time"] jako dict {"seconds": ...}
    - rec["time"] jako tekst: "M:SS.xxx" albo "SS.xxx"
    """
    # 1) jeśli masz już time_seconds – traktuj jako prawdę
    ts = rec.get("time_seconds")
    if isinstance(ts, (int, float)):
        return float(ts)

    t = rec.get("time")

    # 2) liczba
    if isinstance(t, (int, float)):
        return float(t)

    # 3) dict z seconds
    if isinstance(t, dict):
        sec = t.get("seconds")
        if isinstance(sec, (int, float)):
            return float(sec)
        txt = t.get("text")
    else:
        txt = t

    if txt is None:
        return None

    s = str(txt).strip()
    if not s:
        return None

    # 4) parsuj "M:SS.xxx" lub "SS.xxx"
    m = re.match(r"^(?:(\d+):)?(\d+(?:\.\d+)?)$", s)
    if not m:
        return None

    minutes = int(m.group(1)) if m.group(1) else 0
    seconds = float(m.group(2))
    return minutes * 60.0 + seconds

def _record_key(rec: Dict[str, Any]) -> Optional[tuple]:
    """
    Klucz do rozpoznawania tego samego rekordu:

    (driver_text, vehicle_text, year, time_seconds)

    - driver: rec["driver"]["text"] / rec["driver"]
    - vehicle: rec["vehicle"]["text"] / rec["car"]["text"]
    - year: rec["year"] albo rok z rec["date"]["iso"]
    - time: seconds lub sparsowany MM:SS.xxx

    UWAGA: series/category/class NIE jest częścią klucza – jeśli
    wszystko powyższe się zgadza, a różni się tylko series/category,
    traktujemy rekordy jako ten sam lap record.
    """
    driver_txt = _safe_text(rec.get("driver"))

    vehicle_obj = rec.get("vehicle") or rec.get("car")
    vehicle_txt = _safe_text(vehicle_obj)

    # year: najpierw pole year, potem date.iso, potem event
    year: Optional[str] = None
    if rec.get("year") is not None:
        year = str(rec["year"])
    else:
        date_obj = rec.get("date")
        if isinstance(date_obj, dict):
            iso = (date_obj.get("iso") or "").strip()
            if iso:
                year = iso[:4]

    if not year:
        year = _extract_year_from_event(rec)

    time_sec = _time_seconds(rec)

    if not driver_txt or not vehicle_txt or not year or time_sec is None:
        return None

    # round dla stabilności klucza (minimalne różnice floatów)
    return (driver_txt, vehicle_txt, year, round(time_sec, 6))

def _core_key(rec: Dict[str, Any]) -> Optional[tuple]:
    """
    Klucz „rdzeniowy” do łączenia rekordów nawet jeśli brakuje time.

    (driver_text, vehicle_text, year)

    - vehicle może być ucięty → dopasujemy fallbackiem prefiksowym w merge
    """
    driver_txt = _safe_text(rec.get("driver"))
    vehicle_obj = rec.get("vehicle") or rec.get("car")
    vehicle_txt = _safe_text(vehicle_obj)

    year: Optional[str] = None
    if rec.get("year") is not None:
        year = str(rec["year"])
    else:
        date_obj = rec.get("date")
        if isinstance(date_obj, dict):
            iso = (date_obj.get("iso") or "").strip()
            if iso:
                year = iso[:4]

    if not year:
        year = _extract_year_from_event(rec)

    if not driver_txt or not vehicle_txt or not year:
        return None

    return (driver_txt, vehicle_txt, year)

def _norm_vehicle_text(v: Any) -> str:
    if isinstance(v, dict):
        v = v.get("text") or ""
    s = str(v or "").strip().lower()
    s = " ".join(s.split())
    return s

def _vehicle_prefix_match(a: Any, b: Any, *, min_len: int = 10) -> bool:
    va = _norm_vehicle_text(a)
    vb = _norm_vehicle_text(b)
    if not va or not vb:
        return False
    if len(va) < min_len or len(vb) < min_len:
        return False
    return va.startswith(vb) or vb.startswith(va)

def _merge_two_records(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scala dwa rekordy w jeden, preferując bogatsze dane:
    - driver/vehicle: preferuj dict z url
    - series: wybierz najlepsze przez _select_best_series([..])
    - date/year: wybierz najlepsze przez _select_best_date_year([..]) + fallback z event
    - event/pozostałe: pierwszy niepusty
    - time: zawsze float w sekundach
    """
    merged: Dict[str, Any] = dict(base)

    # driver / vehicle (preferuj z URL)
    for key in ("driver",):
        a = base.get(key)
        b = extra.get(key)
        if isinstance(a, dict) and a.get("url"):
            merged[key] = a
        elif b is not None:
            merged[key] = b

    # vehicle może być w vehicle albo car
    a_v = base.get("vehicle") or base.get("car")
    b_v = extra.get("vehicle") or extra.get("car")
    if isinstance(a_v, dict) and a_v.get("url"):
        merged["vehicle"] = a_v
    elif b_v is not None:
        merged["vehicle"] = b_v

    # time -> sekundy
    t = _time_seconds(base)
    if t is None:
        t = _time_seconds(extra)
    if t is not None:
        merged["time"] = float(t)
    merged.pop("time_seconds", None)

    # date / year
    best_date, best_year = _select_best_date_year([base, extra])
    if best_year is None:
        best_year = _extract_year_from_event(base) or _extract_year_from_event(extra)

    if best_date is not None:
        merged["date"] = best_date
        merged.pop("year", None)
    elif best_year is not None:
        merged["year"] = best_year

    # series/category/class -> series
    best_series = _select_best_series([base, extra])
    if best_series is not None:
        merged["series"] = best_series
    merged.pop("category", None)
    merged.pop("class", None)
    merged.pop("class_", None)

    # event i inne pola: pierwszy niepusty
    for k, v in extra.items():
        if k in {"time_seconds", "category", "class", "class_"}:
            continue
        if merged.get(k) is None and v is not None:
            merged[k] = v

    return merged

def _merge_race_lap_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Łączy duplikujące się rekordy (infobox + tabela) w jeden bogaty rekord.

    Etap A: twardy merge po _record_key (driver+vehicle+year+time).
    Etap B: merge po _core_key (driver+vehicle+year) – pozwala łączyć brakujące time.
    Etap C: fallback merge dla uciętych vehicle / braków year (driver+time + prefiks vehicle).
    """
    # --- Etap A: twarde buckety po _record_key
    key_buckets: Dict[tuple, List[Dict[str, Any]]] = {}
    leftovers: List[Dict[str, Any]] = []

    for rec in records:
        k = _record_key(rec)
        if k is None:
            leftovers.append(rec)
        else:
            key_buckets.setdefault(k, []).append(rec)

    merged_main: List[Dict[str, Any]] = [_merge_record_group(rs) for rs in key_buckets.values()]

    # --- Etap B: spróbuj dołączyć leftovers po _core_key (nie wymaga time)
    core_index: Dict[tuple, List[int]] = {}
    for i, rec in enumerate(merged_main):
        ck = _core_key(rec)
        if ck is not None:
            core_index.setdefault(ck, []).append(i)

    still_left: List[Dict[str, Any]] = []
    for rec in leftovers:
        ck = _core_key(rec)
        if ck is None:
            still_left.append(rec)
            continue

        cand_ids = core_index.get(ck, [])
        if not cand_ids:
            still_left.append(rec)
            continue

        # jeśli jest kilka kandydatów (rzadkie), spróbuj dopasować po time jeśli rec ma time
        rec_t = _time_seconds(rec)
        chosen_idx = None
        if rec_t is not None:
            for idx in cand_ids:
                tgt_t = _time_seconds(merged_main[idx])
                if tgt_t is not None and round(float(tgt_t), 6) == round(float(rec_t), 6):
                    chosen_idx = idx
                    break

        # fallback: pierwszy kandydat
        if chosen_idx is None:
            chosen_idx = cand_ids[0]

        merged_main[chosen_idx] = _merge_two_records(merged_main[chosen_idx], rec)

    # --- Etap C: dodatkowy fallback (driver+time + prefiks vehicle) dla uciętych wartości
    index_dt: Dict[tuple, List[int]] = {}
    for i, rec in enumerate(merged_main):
        d = _safe_text(rec.get("driver"))
        t = _time_seconds(rec)
        if d and t is not None:
            index_dt.setdefault((d, round(float(t), 6)), []).append(i)

    final_left: List[Dict[str, Any]] = []
    for rec in still_left:
        d = _safe_text(rec.get("driver"))
        t = _time_seconds(rec)
        if not d or t is None:
            final_left.append(rec)
            continue

        cand_ids = index_dt.get((d, round(float(t), 6)), [])
        if not cand_ids:
            final_left.append(rec)
            continue

        v = rec.get("vehicle") or rec.get("car")
        matched = False
        for idx in cand_ids:
            target = merged_main[idx]
            tv = target.get("vehicle") or target.get("car")
            if _vehicle_prefix_match(v, tv, min_len=10):
                merged_main[idx] = _merge_two_records(target, rec)
                matched = True
                break

        if not matched:
            final_left.append(rec)

    # --- Etap D: fallback dla rekordów typu tylko (driver+time)
    # indeks po time -> kandydaci w merged_main
    time_index: Dict[float, List[int]] = {}
    for i, rec in enumerate(merged_main):
        t = _time_seconds(rec)
        if t is None:
            continue
        time_index.setdefault(round(float(t), 6), []).append(i)

    last_left: List[Dict[str, Any]] = []
    for rec in final_left:
        t = _time_seconds(rec)
        if t is None:
            last_left.append(rec)
            continue

        cand_ids = time_index.get(round(float(t), 6), [])
        if not cand_ids:
            last_left.append(rec)
            continue

        matched = False
        for idx in cand_ids:
            target = merged_main[idx]

            # driver luźno + small jest podzbiorem target -> bezpiecznie scal
            if _driver_loose_match(rec.get("driver"), target.get("driver")) and _is_subset_record(rec, target):
                merged_main[idx] = _merge_two_records(target, rec)
                matched = True
                break

        if not matched:
            last_left.append(rec)

    return merged_main + last_left

def _select_best_driver(records: List[Dict[str, Any]]) -> Optional[Any]:
    """Wybiera najlepszy rekord kierowcy (preferuje wersję z URL)."""
    best = None
    for r in records:
        d = r.get("driver")
        if not d:
            continue
        if best is None:
            best = d
            continue
        # preferuj driver jako dict z URL
        if isinstance(d, dict) and d.get("url") and (
            not isinstance(best, dict) or not best.get("url")
        ):
            best = d
    return best

def _select_best_vehicle(records: List[Dict[str, Any]]) -> Optional[Any]:
    """Wybiera najlepszy rekord pojazdu (preferuje wersję z URL)."""
    best = None
    for r in records:
        v = r.get("vehicle") or r.get("car")
        if not v:
            continue
        if best is None:
            best = v
            continue
        # preferuj wersję z linkiem
        if isinstance(v, dict) and v.get("url") and (
            not isinstance(best, dict) or not best.get("url")
        ):
            best = v
    return best

def _select_best_time(records: List[Dict[str, Any]]) -> Optional[float]:
    """
    Zwraca czas WYŁĄCZNIE jako sekundy (float).

    Obsługuje:
    - float/int (już sekundy),
    - str typu "1:35.895" albo "38.891",
    - dict z TimeColumn: {"text": "...", "seconds": ...}.
    """
    # korzystamy z istniejącej logiki klucza czasu (ona już umie parsować stringi itp.)
    for r in records:
        tk = _time_key(r)
        if isinstance(tk, (int, float)):
            return float(tk)

    # fallback (gdyby _time_key zwrócił string w nietypowym przypadku)
    for r in records:
        t = r.get("time")
        if isinstance(t, dict):
            sec = t.get("seconds")
            if isinstance(sec, (int, float)):
                return float(sec)
        if isinstance(t, (int, float)):
            return float(t)
        if isinstance(t, str):
            try:
                return float(t.strip())
            except ValueError:
                continue

    return None

def _select_best_date_year(records: List[Dict[str, Any]]) -> Tuple[Optional[Any], Optional[Any]]:
    """Wybiera najlepszą datę i rok (preferuje dokładniejszy iso)."""
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

    return best_date, best_year

def _select_best_series(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Wybiera najlepszą serię/kategorię (preferuje wersję z linkiem)."""
    def series_candidate(r: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        cand = r.get("series") or r.get("category") or r.get("class") or r.get("class_")
        if cand is None:
            return None
        if isinstance(cand, dict):
            return {
                "text": (cand.get("text") or cand.get("name") or "").strip(),
                "url": cand.get("url"),
            }
        return {"text": str(cand).strip(), "url": None}

    best = None
    best_has_url = False
    best_len = 0

    for r in records:
        cand = series_candidate(r)
        if not cand:
            continue

        text = (cand.get("text") or "").strip()
        has_url = bool(cand.get("url"))
        text_len = len(text)

        if best is None:
            best = cand
            best_has_url = has_url
            best_len = text_len
            continue

        # jeśli ten ma URL, a dotychczasowy nie – bierzemy ten
        if has_url and not best_has_url:
            best = cand
            best_has_url = True
            best_len = text_len
            continue

        # jeśli oba mają (albo oba nie mają) URL – wybieramy dłuższą nazwę
        if has_url == best_has_url and text_len > best_len:
            best = cand
            best_len = text_len

    return best

def _collect_other_fields(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Zbiera pozostałe pola, ale NIE przenosi dubli typu:
    - time_seconds (bo wynikowo i tak będzie time w sekundach)
    - category/class (bo wynikowo i tak będzie series)
    """
    ignore_keys = {
        "driver",
        "vehicle",
        "car",
        "time",
        "time_seconds",
        "date",
        "year",
        "series",
        "category",
        "class",
        "class_",
    }

    merged: Dict[str, Any] = {}
    for r in records:
        for k, v in r.items():
            if k in ignore_keys:
                continue
            if k not in merged and v is not None:
                merged[k] = v
    return merged

def _merge_record_group(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Wynik:
    - time: float (sekundy)  ✅ (bez time_seconds)
    - series: dict{text,url} ✅ (z category/class)
    - year: jeśli brak date, bierzemy year (również z event)
    """
    merged = _collect_other_fields(records)

    best_driver = _select_best_driver(records)
    best_vehicle = _select_best_vehicle(records)
    best_date, best_year = _select_best_date_year(records)
    best_series = _select_best_series(records)

    # time zawsze w sekundach (float)
    # bierzemy pierwsze sensowne z grupy (one są tym samym rekordem)
    t = None
    for r in records:
        t = _time_seconds(r)
        if t is not None:
            break

    # year fallback z event (gdy nadal brak)
    if best_year is None:
        for r in records:
            y = _extract_year_from_event(r)
            if y:
                best_year = y
                break

    if best_driver is not None:
        merged["driver"] = best_driver
    if best_vehicle is not None:
        merged["vehicle"] = best_vehicle
    if t is not None:
        merged["time"] = float(t)

    if best_date is not None:
        merged["date"] = best_date
    elif best_year is not None:
        merged["year"] = best_year

    if best_series is not None:
        merged["series"] = best_series

    return merged

def _extract_circuit_names(raw: Dict[str, Any], infobox: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
    """Ekstrakcja nazwy i poprzednich nazw toru."""
    circuit = raw.get("circuit") or {}
    name_set: set[str] = set()
    name_list: List[str] = []

    # 1) circuit[text] -> name.list
    _add_name(name_set, name_list, circuit.get("text"))

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

    return {
        "list": name_list,
        "former_names": former_names,
    }

def _extract_circuit_url(raw: Dict[str, Any], details: Optional[Dict[str, Any]]) -> Optional[str]:
    """Ekstrakcja URL toru (None jeśli brak szczegółów)."""
    circuit = raw.get("circuit") or {}
    if details is None:
        return None
    return circuit.get("url")

def _extract_circuit_location(raw: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
    """Ekstrakcja lokalizacji toru z konsolidacją miejsc i współrzędnych."""
    country = raw.get("country")
    old_location = raw.get("location")
    new_location = normalized.get("location") if normalized else None
    coordinates = normalized.get("coordinates") if normalized else None

    def extract_place(text: Optional[str], url: Optional[str]) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        clean = text.strip()
        if not clean:
            return None
        return {"text": clean, "url": url}

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

    return {
        "places": list(places_map.values()),
        "coordinates": coordinates,
    }

def _extract_circuit_grade_and_history(normalized: Dict[str, Any]) -> tuple[Optional[str], Optional[List[Any]]]:
    """Ekstrakcja klasy FIA i historii zdarzeń."""
    if not normalized:
        return None, None

    specs = normalized.get("specs") or {}
    fia_grade = specs.get("fia_grade")
    
    history_norm = normalized.get("history") or {}
    history_events = history_norm.get("events")

    return fia_grade, history_events

def _extract_infobox_layouts(infobox: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Ekstrakcja layoutów z infoboxu i konwersja race_lap_record na listę."""
    layouts: List[Dict[str, Any]] = []
    if not infobox:
        return layouts

    for layout in infobox.get("layouts") or []:
        lay = dict(layout)
        rlr = lay.pop("race_lap_record", None)
        records: List[Dict[str, Any]] = []
        if rlr is not None:
            records.append(rlr)
        lay["race_lap_records"] = records
        layouts.append(lay)

    return layouts

def _parse_table_layout_info(table_layout: str) -> tuple[Optional[float], Optional[str]]:
    """Parsuje informacje o długości i latach z tekstu layoutu tabeli."""
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

    return length_km, years_str

def _find_layout_for_table(table_layout: str, layouts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Dopasowuje layout z tabeli do layoutu z infoboxa na podstawie:
    - długości okrążenia (km),
    - lat obowiązywania layoutu.
    """
    if not table_layout:
        return None

    length_km, years_str = _parse_table_layout_info(table_layout)
    best_candidate: Optional[Dict[str, Any]] = None

    for lay in layouts:
        lay_len = lay.get("length_km")
        lay_years_raw = lay.get("years") or ""
        lay_years = lay_years_raw.strip().lower()

        # 1) dopasowanie długości
        if length_km is not None and lay_len is not None:
            if abs(lay_len - length_km) > 1e-3:
                continue

        # 2) dopasowanie lat
        if years_str and lay_years:
            if years_str == lay_years:
                return lay

            # bardziej miękka heurystyka: porównujemy rok startowy
            y_tab = re.search(r"\d{4}", years_str)
            y_lay = re.search(r"\d{4}", lay_years)
            if y_tab and y_lay and y_tab.group(0) != y_lay.group(0):
                continue

        # jeżeli przeszliśmy powyższe filtry – traktujemy jako kandydata
        if best_candidate is None:
            best_candidate = lay

    return best_candidate

def _merge_tables_into_layouts(tables: List[Dict[str, Any]], layouts: List[Dict[str, Any]]) -> None:
    """Łączy rekordy z tabel w odpowiednie layouty."""
    for table_block in tables:
        t_layout_str = table_block.get("layout")
        lap_records = table_block.get("lap_records") or []
        if not t_layout_str:
            continue

        target_layout = _find_layout_for_table(t_layout_str, layouts)
        if target_layout is None:
            layouts.append(
                {
                    "layout": t_layout_str,
                    "race_lap_records": list(lap_records),
                }
            )
        else:
            target_layout.setdefault("race_lap_records", [])
            target_layout["race_lap_records"].extend(lap_records)

    # deduplikacja i scalanie race_lap_records w ramach każdego layoutu
    for lay in layouts:
        records = lay.get("race_lap_records") or []
        if records:
            lay["race_lap_records"] = _merge_race_lap_records(records)

def _cleanup_urls(obj: Any) -> Any:
    """Usuwa url=None oraz rekursywnie czyści elementy."""
    if isinstance(obj, list):
        return [_cleanup_urls(x) for x in obj if x is not None]

    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if v is None:
                continue
            cv = _cleanup_urls(v)
            if cv == []:
                continue
            if isinstance(cv, dict) and set(cv.keys()) == set():
                continue
            cleaned[k] = cv
        return cleaned

    return obj

def _simplify_time(rec: Dict[str, Any]) -> None:
    """Zamienia time dict na float jeśli jest seconds, albo próbuje zparsować tekstowo."""
    t = rec.get("time")
    if not isinstance(t, dict):
        return

    if "seconds" in t:
        rec["time"] = t["seconds"]
        return

    txt = t.get("text")
    if not txt:
        rec["time"] = None
        return

    m = re.match(r"(?:(\d+):)?(\d+\.\d+|\d+)", txt.strip())
    if m:
        minutes = int(m.group(1)) if m.group(1) else 0
        seconds = float(m.group(2))
        rec["time"] = minutes * 60 + seconds
    else:
        rec["time"] = txt

def _simplify_date(rec: Dict[str, Any]) -> None:
    """Zamienia date dict na wartość "YYYY-MM-DD" lub "YYYY-MM" lub "YYYY"."""
    d = rec.get("date")
    if not isinstance(d, dict):
        return
    iso = d.get("iso")
    if iso:
        rec["date"] = iso
    else:
        txt = d.get("text")
        if txt:
            rec["date"] = txt.strip()

def _remove_empty_lists(obj: Any) -> Any:
    """Rekursywnie usuwa puste listy ze struktury."""
    if isinstance(obj, dict):
        keys_to_del = []
        for k, v in obj.items():
            rv = _remove_empty_lists(v)
            if rv == []:
                keys_to_del.append(k)
            else:
                obj[k] = rv
        for k in keys_to_del:
            del obj[k]
        return obj
    if isinstance(obj, list):
        new_list = [_remove_empty_lists(x) for x in obj]
        return [x for x in new_list if x != []]
    return obj

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

    infobox = None
    normalized = None
    if isinstance(details, dict):
        infobox = (details or {}).get("infobox") or {}
        normalized = infobox.get("normalized") or {}

    # -----------------------
    # name + url
    # -----------------------
    out["name"] = _extract_circuit_names(raw, infobox, normalized)
    out["url"] = _extract_circuit_url(raw, details)

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
    # location
    # -----------------------
    out["location"] = _extract_circuit_location(raw, normalized)

    # -----------------------
    # fia_grade + history (events)
    # -----------------------
    fia_grade, history_events = _extract_circuit_grade_and_history(normalized)
    if fia_grade is not None:
        out["fia_grade"] = fia_grade
    if history_events is not None:
        out["history"] = history_events

    # -----------------------
    # layouts
    # -----------------------
    layouts = _extract_infobox_layouts(infobox)

    # -----------------------
    # tables łączymy z layouts
    # -----------------------
    tables = None
    if isinstance(details, dict):
        tables = details.get("tables")
    tables = tables or []

    _merge_tables_into_layouts(tables, layouts)

    if layouts:
        out["layouts"] = layouts

    # -----------------------
    # FINAL CLEANUP JSON
    # -----------------------

    # Apply cleanup to layout records
    for lay in out.get("layouts", []):
        records = lay.get("race_lap_records", [])
        for r in records:
            _simplify_time(r)
            _simplify_date(r)

    # Clean url=None in whole output
    out = _cleanup_urls(out)

    # Remove empty lists
    out = _remove_empty_lists(out)

    return out

