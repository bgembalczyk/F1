from __future__ import annotations

from typing import Any, Dict, List, Optional

import re
import requests
from bs4 import BeautifulSoup

from f1_http.interfaces import HttpClientProtocol
from scrapers.base.scraper import F1Scraper
from scrapers.circuits.list_scraper import F1CircuitsListScraper
from scrapers.circuits.single_scraper import F1SingleCircuitScraper
from scrapers.base.run import run_and_export


def _add_name(names_set: set[str], name_list: List[str], value: Optional[str]) -> None:
    if not value:
        return
    value = value.strip()
    if value and value not in names_set:
        names_set.add(value)
        name_list.append(value)


def normalize_circuit_record(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizuje pojedynczy rekord toru wg ustalonych zasad:

    - circuit[text] -> name.list (dodajemy też infobox.title i infobox.normalized.name)
    - circuit[url] -> url, ale jeśli details == None -> url = None
    - former_names -> name.former_names
    - layouts z infobox.layouts przenosimy na górę, race_lap_record -> race_lap_records (lista)
    - tables łączymy z layouts (lap_records -> race_lap_records odpowiedniego layoutu)
    - location: { old_location, new_location, coordinates, country }
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
    for key in ("circuit_status", "type", "direction", "grands_prix", "seasons", "grands_prix_held"):
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

    # -----------------------
    # Helpers
    # -----------------------

    def extract_place(text: Optional[str], url: Optional[str]) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        clean = text.strip()
        if not clean:
            return None
        return {"text": clean, "url": url}

    # ordered-set by place text
    places_map: Dict[str, Dict[str, Any]] = {}

    # -----------------------
    # 1) old_location → places
    # -----------------------
    if isinstance(old_location, dict):
        p = extract_place(old_location.get("text"), old_location.get("url"))
        if p:
            places_map[p["text"]] = p

    # -----------------------
    # 2) new_location → places
    # -----------------------
    if isinstance(new_location, dict):
        for key, val in new_location.items():
            if not isinstance(val, dict):
                continue

            text = val.get("text") or val.get("label")
            link = val.get("link") or {}
            url = link.get("url")

            p = extract_place(text, url)
            if p:
                places_map[p["text"]] = p

    # -----------------------
    # 3) country też trafia do places
    # -----------------------
    if country:
        p = extract_place(country, None)
        if p:
            places_map.setdefault(p["text"], p)

    # -----------------------
    # Zapisujemy location BEZ pola "country"
    # -----------------------
    out["location"] = {
        "places": list(places_map.values()),
        "coordinates": coordinates,
    }

    # -----------------------
    # fia_grade na wierzchu
    # -----------------------
    # -----------------------
    # history (tylko lista events)
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
            # zamieniamy przecinek na kropkę na wszelki wypadek
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

    if layouts:
        out["layouts"] = layouts

    return out


class F1CompleteCircuitScraper(F1Scraper):
    """
    Pobiera listę torów, a następnie zaciąga szczegóły każdego toru (infobox + tabele),
    po czym normalizuje rekord do docelowej struktury.

    Dla torów, których artykuł nie ma "circuit/racetrack"-podobnych kategorii,
    pole `url` będzie miało wartość None, a `layouts` / `history` / nowe location
    mogą być puste.
    """

    url = F1CircuitsListScraper.url

    def __init__(
        self,
        *,
        delay_seconds: float = 1.0,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
    ) -> None:
        super().__init__(
            include_urls=True,
            session=session,
            headers=headers,
            http_client=http_client,
        )
        self.delay_seconds = delay_seconds
        self.list_scraper = F1CircuitsListScraper(
            include_urls=True,
            http_client=self.http_client,
        )
        self.single_scraper = F1SingleCircuitScraper(
            http_client=self.http_client,
            delay_seconds=delay_seconds,
        )

    def fetch(self) -> List[Dict[str, Any]]:
        circuits = self.list_scraper.fetch()
        complete: List[Dict[str, Any]] = []

        for circuit in circuits:
            circuit_url: Optional[str] = None
            circuit_data = circuit.get("circuit")
            if isinstance(circuit_data, dict):
                circuit_url = circuit_data.get("url")

            details: Optional[Dict[str, Any]] = None
            if circuit_url:
                details = self.single_scraper.fetch(circuit_url)

            full_record = dict(circuit)
            full_record["details"] = details

            normalized = normalize_circuit_record(full_record)
            complete.append(normalized)

        self._data = complete
        return self._data

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Metoda wymagana przez bazę – nie używana w tym scraperze."""
        raise NotImplementedError("Use fetch() bezpośrednio dla pełnego scrapingu")


if __name__ == "__main__":
    run_and_export(
        F1CompleteCircuitScraper,
        "../../data/wiki/circuits/f1_circuits_extended.json",
        # csv_path pomijamy – jest opcjonalny
        delay_seconds=1.0,
    )
