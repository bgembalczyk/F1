"""Utility functions for loading Ergast CSV exports with basic validation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

import pandas as pd

DEFAULT_BASE_DIR = Path("data/main")


class DatasetValidationError(ValueError):
    """Raised when a dataset is missing required columns."""


@dataclass(frozen=True)
class DatasetSpec:
    filename: str
    required_columns: Sequence[str]

    def resolve_path(self, base_path: Path | str) -> Path:
        base = Path(base_path)
        return base if base.is_file() else base / self.filename


RACES_SPEC = DatasetSpec("races.csv", ["raceId", "year", "circuitId"])
RESULTS_SPEC = DatasetSpec(
    "results.csv", ["raceId", "driverId", "constructorId", "positionOrder"]
)
DRIVERS_SPEC = DatasetSpec("drivers.csv", ["driverId", "forename", "surname"])
CONSTRUCTORS_SPEC = DatasetSpec("constructors.csv", ["constructorId", "name"])
CIRCUITS_SPEC = DatasetSpec("circuits.csv", ["circuitId", "name"])
CONSTRUCTOR_STANDINGS_SPEC = DatasetSpec(
    "constructor_standings.csv",
    ["constructorStandingsId", "raceId", "constructorId", "points"],
)


def _load_dataset(spec: DatasetSpec, base_path: Path | str = DEFAULT_BASE_DIR) -> pd.DataFrame:
    dataset_path = spec.resolve_path(base_path)
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path)
    missing = _missing_columns(df.columns, spec.required_columns)
    if missing:
        raise DatasetValidationError(
            f"Dataset {dataset_path} is missing required columns: {', '.join(sorted(missing))}"
        )
    return df[list(spec.required_columns)].copy()


def _missing_columns(columns: Iterable[str], required: Sequence[str]) -> List[str]:
    present = set(columns)
    return [column for column in required if column not in present]


def load_races(base_path: Path | str = DEFAULT_BASE_DIR) -> pd.DataFrame:
    """Load race data with race/circuit identifiers and year."""

    return _load_dataset(RACES_SPEC, base_path)


def load_results(base_path: Path | str = DEFAULT_BASE_DIR) -> pd.DataFrame:
    """Load race results with finishing positions."""

    return _load_dataset(RESULTS_SPEC, base_path)


def load_drivers(base_path: Path | str = DEFAULT_BASE_DIR) -> pd.DataFrame:
    """Load driver names and identifiers."""

    return _load_dataset(DRIVERS_SPEC, base_path)


def load_constructors(base_path: Path | str = DEFAULT_BASE_DIR) -> pd.DataFrame:
    """Load constructor names and identifiers."""

    return _load_dataset(CONSTRUCTORS_SPEC, base_path)


def load_circuits(base_path: Path | str = DEFAULT_BASE_DIR) -> pd.DataFrame:
    """Load circuit names and identifiers."""

    return _load_dataset(CIRCUITS_SPEC, base_path)


def load_constructor_standings(base_path: Path | str = DEFAULT_BASE_DIR) -> pd.DataFrame:
    """Load constructor standings for each race."""

    return _load_dataset(CONSTRUCTOR_STANDINGS_SPEC, base_path)
