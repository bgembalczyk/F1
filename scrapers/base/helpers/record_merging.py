"""Funkcje do scalania i selekcji rekordów."""

from __future__ import annotations
from typing import Any

from scrapers.base.helpers.record_keys import (
    extract_year_from_event,
    record_key,
    core_key,
)
from scrapers.base.helpers.text_processing import (
    driver_loose_match,
    vehicle_prefix_match,
    safe_text,
)
from scrapers.base.helpers.time_processing import time_seconds


def is_subset_record(small: dict[str, Any], big: dict[str, Any]) -> bool:
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
            st = time_seconds(
                {"time": sv} if not isinstance(sv, dict) else {"time": sv}
            )
            bt = time_seconds(
                {"time": bv} if not isinstance(bv, dict) else {"time": bv}
            )
            if st is None or bt is None:
                continue
            if round(float(st), 6) != round(float(bt), 6):
                return False
            continue

        # driver/vehicle porównujemy po tekście (luźno)
        if k == "driver":
            if not driver_loose_match(sv, bv):
                return False
            continue
        if k in ("vehicle", "car"):
            # jeśli small ma vehicle, a big też, to prefix match OK
            if not vehicle_prefix_match(sv, bv, min_len=6):
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

def merge_two_records(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """
    Scala dwa rekordy w jeden, preferując bogatsze dane:
    - driver/vehicle: preferuj dict z url
    - series: wybierz najlepsze przez select_best_series([..])
    - date/year: wybierz najlepsze przez select_best_date_year([..]) + fallback z event
    - event/pozostałe: pierwszy niepusty
    - time: zawsze float w sekundach
    """
    merged: dict[str, Any] = dict(base)

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
    t = time_seconds(base)
    if t is None:
        t = time_seconds(extra)
    if t is not None:
        merged["time"] = float(t)
    merged.pop("time_seconds", None)

    # date / year
    best_date, best_year = select_best_date_year([base, extra])
    if best_year is None:
        best_year = extract_year_from_event(base) or extract_year_from_event(extra)

    if best_date is not None:
        merged["date"] = best_date
        merged.pop("year", None)
    elif best_year is not None:
        merged["year"] = best_year

    # series/category/class -> series
    best_series = select_best_series([base, extra])
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

def collect_other_fields(records: list[dict[str, Any]]) -> dict[str, Any]:
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

    merged: dict[str, Any] = {}
    for r in records:
        for k, v in r.items():
            if k in ignore_keys:
                continue
            if k not in merged and v is not None:
                merged[k] = v
    return merged

def select_best_driver(records: list[dict[str, Any]]) -> Any:
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
        if (
            isinstance(d, dict)
            and d.get("url")
            and (not isinstance(best, dict) or not best.get("url"))
        ):
            best = d
    return best

def select_best_vehicle(records: list[dict[str, Any]]) -> Any:
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
        if (
            isinstance(v, dict)
            and v.get("url")
            and (not isinstance(best, dict) or not best.get("url"))
        ):
            best = v
    return best

def select_best_time(records: list[dict[str, Any]]) -> float | None:
    """
    Zwraca czas WYŁĄCZNIE jako sekundy (float).

    Obsługuje:
    - float/int (już sekundy),
    - str typu "1:35.895" albo "38.891",
    - dict z TimeColumn: {"text": "...", "seconds": ...}.
    """
    # korzystamy z istniejącej logiki klucza czasu (ona już umie parsować stringi itp.)
    from .time_processing import time_key

    for r in records:
        tk = time_key(r)
        if isinstance(tk, (int, float)):
            return float(tk)

    # fallback (gdyby time_key zwrócił string w nietypowym przypadku)
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

def select_best_date_year(records: list[dict[str, Any]]) -> tuple[Any, Any]:
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

def select_best_series(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Wybiera najlepszą serię/kategorię (preferuje wersję z linkiem)."""

    def series_candidate(r: dict[str, Any]) -> dict[str, Any] | None:
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

def merge_record_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Wynik:
    - time: float (sekundy)  ✅ (bez time_seconds)
    - series: dict{text,url} ✅ (z category/class)
    - year: jeśli brak date, bierzemy year (również z event)
    """
    merged = collect_other_fields(records)

    best_driver = select_best_driver(records)
    best_vehicle = select_best_vehicle(records)
    best_date, best_year = select_best_date_year(records)
    best_series = select_best_series(records)

    # time zawsze w sekundach (float)
    # bierzemy pierwsze sensowne z grupy (one są tym samym rekordem)
    t = None
    for r in records:
        t = time_seconds(r)
        if t is not None:
            break

    # year fallback z event (gdy nadal brak)
    if best_year is None:
        for r in records:
            y = extract_year_from_event(r)
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

def merge_race_lap_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Łączy duplikujące się rekordy (infobox + tabela) w jeden bogaty rekord.

    Etap A: twardy merge po record_key (driver+vehicle+year+time).
    Etap B: merge po core_key (driver+vehicle+year) – pozwala łączyć brakujące time.
    Etap C: fallback merge dla uciętych vehicle / braków year (driver+time + prefiks vehicle).
    """
    # --- Etap A: twarde buckety po record_key
    key_buckets: dict[tuple, list[dict[str, Any]]] = {}
    leftovers: list[dict[str, Any]] = []

    for rec in records:
        k = record_key(rec)
        if k is None:
            leftovers.append(rec)
        else:
            key_buckets.setdefault(k, []).append(rec)

    merged_main: list[dict[str, Any]] = [
        merge_record_group(rs) for rs in key_buckets.values()
    ]

    # --- Etap B: spróbuj dołączyć leftovers po core_key (nie wymaga time)
    core_index: dict[tuple, list[int]] = {}
    for i, rec in enumerate(merged_main):
        ck = core_key(rec)
        if ck is not None:
            core_index.setdefault(ck, []).append(i)

    still_left: list[dict[str, Any]] = []
    for rec in leftovers:
        ck = core_key(rec)
        if ck is None:
            still_left.append(rec)
            continue

        cand_ids = core_index.get(ck, [])
        if not cand_ids:
            still_left.append(rec)
            continue

        # jeśli jest kilka kandydatów (rzadkie), spróbuj dopasować po time jeśli rec ma time
        rec_t = time_seconds(rec)
        chosen_idx = None
        if rec_t is not None:
            for idx in cand_ids:
                tgt_t = time_seconds(merged_main[idx])
                if tgt_t is not None and round(float(tgt_t), 6) == round(
                    float(rec_t), 6
                ):
                    chosen_idx = idx
                    break

        # fallback: pierwszy kandydat
        if chosen_idx is None:
            chosen_idx = cand_ids[0]

        merged_main[chosen_idx] = merge_two_records(merged_main[chosen_idx], rec)

    # --- Etap C: dodatkowy fallback (driver+time + prefiks vehicle) dla uciętych wartości
    index_dt: dict[tuple, list[int]] = {}
    for i, rec in enumerate(merged_main):
        d = safe_text(rec.get("driver"))
        t = time_seconds(rec)
        if d and t is not None:
            index_dt.setdefault((d, round(float(t), 6)), []).append(i)

    final_left: list[dict[str, Any]] = []
    for rec in still_left:
        d = safe_text(rec.get("driver"))
        t = time_seconds(rec)
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
            if vehicle_prefix_match(v, tv, min_len=10):
                merged_main[idx] = merge_two_records(target, rec)
                matched = True
                break

        if not matched:
            final_left.append(rec)

    # --- Etap D: fallback dla rekordów typu tylko (driver+time)
    # indeks po time -> kandydaci w merged_main
    time_index: dict[float, list[int]] = {}
    for i, rec in enumerate(merged_main):
        t = time_seconds(rec)
        if t is None:
            continue
        time_index.setdefault(round(float(t), 6), []).append(i)

    last_left: list[dict[str, Any]] = []
    for rec in final_left:
        t = time_seconds(rec)
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
            if driver_loose_match(
                rec.get("driver"), target.get("driver")
            ) and is_subset_record(rec, target):
                merged_main[idx] = merge_two_records(target, rec)
                matched = True
                break

        if not matched:
            last_left.append(rec)

    return merged_main + last_left
