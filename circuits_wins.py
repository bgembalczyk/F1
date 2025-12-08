import argparse
from pathlib import Path

import pandas as pd

from data.ergast_loader import (
    load_circuits,
    load_constructors,
    load_drivers,
    load_races,
    load_results,
)


def compute_circuit_wins(
    races: pd.DataFrame,
    results: pd.DataFrame,
    drivers: pd.DataFrame,
    constructors: pd.DataFrame,
    circuits: pd.DataFrame,
) -> pd.DataFrame:
    data = (
        results.merge(races, on="raceId", how="left")
        .merge(drivers, on="driverId", how="left")
        .merge(constructors, on="constructorId", how="left")
        .merge(circuits, on="circuitId", how="left", suffixes=("", "_circuit"))
    )

    winners = data[data["positionOrder"] == 1]
    circuit_wins = (
        winners.groupby(["circuitId", "name_circuit", "driverId", "forename", "surname"])
        .size()
        .reset_index(name="wins")
    )
    return circuit_wins.sort_values(by="wins", ascending=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate per-circuit win counts for drivers from Ergast CSV exports.",
    )
    parser.add_argument(
        "--base-dir",
        default=Path("data/main"),
        type=Path,
        help="Directory containing Ergast CSV files (races/results/constructors/drivers/circuits).",
    )
    parser.add_argument(
        "--output",
        default=Path("data/circuits_wins.csv"),
        type=Path,
        help="Path to save the aggregated CSV with circuit wins.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top rows to preview after aggregation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    races = load_races(args.base_dir)
    results = load_results(args.base_dir)
    drivers = load_drivers(args.base_dir)
    constructors = load_constructors(args.base_dir)
    circuits = load_circuits(args.base_dir)

    circuit_wins = compute_circuit_wins(races, results, drivers, constructors, circuits)
    circuit_wins.to_csv(args.output, index=False)

    preview = circuit_wins.head(args.top_n) if args.top_n > 0 else circuit_wins
    print(preview)


if __name__ == "__main__":
    main()
