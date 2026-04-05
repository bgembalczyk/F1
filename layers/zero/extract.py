"""Layer Zero Phase C: Copy B_merge files and extract cross-domain references."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from layers.path_resolver import PathResolver


def extract_layer_zero_phase_c(base_wiki_dir: Path) -> None:
    """Phase C: copy B_merge files to C_extract and extract cross-domain references."""
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    resolver = PathResolver(layer_zero_root=layer_zero_dir)

    _copy_b_merge_to_c_extract(layer_zero_dir, resolver)
    _extract_cross_domain_references(layer_zero_dir, resolver)


def _copy_b_merge_to_c_extract(layer_zero_dir: Path, resolver: PathResolver) -> None:
    for domain_dir in sorted(p for p in layer_zero_dir.iterdir() if p.is_dir()):
        merged_file = resolver.merged(domain=domain_dir.name)
        if not merged_file.exists():
            continue
        extract_dir = resolver.extract_dir(domain=domain_dir.name)
        extract_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(merged_file, extract_dir / merged_file.name)


def _read_b_merge(
    domain_dir: Path,
    resolver: PathResolver,
) -> list[object] | None:
    merged_file = resolver.merged(domain=domain_dir.name)
    if not merged_file.exists():
        return None
    data = json.loads(merged_file.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else None


def _write_c_extract_file(
    target_domain: str,
    filename: str,
    values: list[object],
    resolver: PathResolver,
) -> None:
    if not values:
        return
    extract_dir = resolver.extract_dir(domain=target_domain)
    extract_dir.mkdir(parents=True, exist_ok=True)
    out_path = extract_dir / filename
    out_path.write_text(
        json.dumps(values, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _get_formula_one(record: dict[str, object]) -> dict[str, object] | None:
    racing_series = record.get("racing_series")
    if not isinstance(racing_series, dict):
        return None
    formula_one = racing_series.get("formula_one")
    if not isinstance(formula_one, dict):
        return None
    return formula_one


def _extract_cross_domain_references(
    layer_zero_dir: Path,
    resolver: PathResolver,
) -> None:
    _extract_from_chassis_constructors(layer_zero_dir, resolver)
    _extract_from_circuits(layer_zero_dir, resolver)
    _extract_from_constructors(layer_zero_dir, resolver)
    _extract_from_drivers(layer_zero_dir, resolver)
    _extract_from_engines(layer_zero_dir, resolver)
    _extract_from_races(layer_zero_dir, resolver)


def _extract_from_chassis_constructors(
    layer_zero_dir: Path,
    resolver: PathResolver,
) -> None:
    records = _read_b_merge(layer_zero_dir / "chassis_constructors", resolver)
    if not records:
        return

    countries: list[object] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        licensed_in = record.get("licensed_in")
        if isinstance(licensed_in, list):
            countries.extend(licensed_in)
        elif licensed_in is not None:
            countries.append(licensed_in)

    _write_c_extract_file("countries", "from_chassis_constructors.json", countries, resolver)


def _extract_from_circuits(
    layer_zero_dir: Path,
    resolver: PathResolver,
) -> None:
    records = _read_b_merge(layer_zero_dir / "circuits", resolver)
    if not records:
        return

    countries: list[object] = []
    locations: list[object] = []

    for record in records:
        if not isinstance(record, dict):
            continue
        country = record.get("country")
        if country is not None:
            countries.append(country)
        location = record.get("location")
        if location is not None:
            locations.append(location)

    _write_c_extract_file("countries", "from_circuits.json", countries, resolver)
    _write_c_extract_file("locations", "from_circuits.json", locations, resolver)


def _extract_from_constructors(
    layer_zero_dir: Path,
    resolver: PathResolver,
) -> None:
    records = _read_b_merge(layer_zero_dir / "constructors", resolver)
    if not records:
        return

    engines: list[object] = []
    teams: list[object] = []
    countries: list[object] = []

    for record in records:
        if not isinstance(record, dict):
            continue

        engine = record.get("engine")
        if isinstance(engine, list):
            engines.extend(engine)
        elif engine is not None:
            engines.append(engine)

        formula_one = _get_formula_one(record)
        if formula_one is None:
            continue

        antecedent_teams = formula_one.get("antecedent_teams")
        if isinstance(antecedent_teams, list):
            teams.extend(antecedent_teams)
        elif antecedent_teams is not None:
            teams.append(antecedent_teams)

        based_in = formula_one.get("based_in")
        if isinstance(based_in, list):
            countries.extend(based_in)
        elif based_in is not None:
            countries.append(based_in)

        licensed_in = formula_one.get("licensed_in")
        if isinstance(licensed_in, list):
            countries.extend(licensed_in)
        elif licensed_in is not None:
            countries.append(licensed_in)

    _write_c_extract_file("engines", "from_constructors.json", engines, resolver)
    _write_c_extract_file("teams", "from_constructors.json", teams, resolver)
    _write_c_extract_file("countries", "from_constructors.json", countries, resolver)


def _extract_from_drivers(
    layer_zero_dir: Path,
    resolver: PathResolver,
) -> None:
    records = _read_b_merge(layer_zero_dir / "drivers", resolver)
    if not records:
        return

    countries: list[object] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        nationality = record.get("nationality")
        if nationality is not None:
            countries.append(nationality)

    _write_c_extract_file("countries", "from_drivers.json", countries, resolver)


def _extract_from_engines(
    layer_zero_dir: Path,
    resolver: PathResolver,
) -> None:
    records = _read_b_merge(layer_zero_dir / "engines", resolver)
    if not records:
        return

    countries: list[object] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        formula_one = _get_formula_one(record)
        if formula_one is None:
            continue
        engines_built_in = formula_one.get("engines_built_in")
        if isinstance(engines_built_in, list):
            countries.extend(engines_built_in)
        elif engines_built_in is not None:
            countries.append(engines_built_in)

    _write_c_extract_file("countries", "from_engines.json", countries, resolver)


def _extract_from_races(
    layer_zero_dir: Path,
    resolver: PathResolver,
) -> None:
    records = _read_b_merge(layer_zero_dir / "races", resolver)
    if not records:
        return

    drivers: list[object] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        red_flag = record.get("red_flag")
        if not isinstance(red_flag, dict):
            continue

        winner = red_flag.get("winner")
        if winner is not None:
            drivers.append(winner)

        failed_to_make_restart = red_flag.get("failed_to_make_restart")
        if isinstance(failed_to_make_restart, list):
            for entry in failed_to_make_restart:
                if not isinstance(entry, dict):
                    continue
                entry_drivers = entry.get("drivers")
                if isinstance(entry_drivers, list):
                    drivers.extend(entry_drivers)
                elif entry_drivers is not None:
                    drivers.append(entry_drivers)

    _write_c_extract_file("drivers", "from_races.json", drivers, resolver)
