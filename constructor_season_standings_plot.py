import argparse
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from data.ergast_loader import (
    load_constructor_standings,
    load_constructors,
    load_races,
)


def build_constructor_points(
    races: pd.DataFrame,
    constructor_standings: pd.DataFrame,
    constructors: pd.DataFrame,
    top_n: int,
) -> pd.DataFrame:
    standings = constructor_standings[["raceId", "constructorId", "points"]].copy()
    df = standings.merge(races[["raceId", "year"]], on="raceId", how="left").merge(
        constructors[["constructorId", "name"]], on="constructorId", how="left"
    )

    season_points = df.groupby(["year", "constructorId"])["points"].max().reset_index()
    total_points = season_points.groupby("constructorId")["points"].sum().reset_index()
    total_points = total_points.merge(
        constructors[["constructorId", "name"]], on="constructorId"
    )

    top_teams = (
        total_points.sort_values("points", ascending=False)
        .head(top_n)
        .set_index("constructorId")
    )
    top_teams_ids = top_teams.index

    top_teams_seasons = season_points[season_points["constructorId"].isin(top_teams_ids)]
    top_teams_seasons = top_teams_seasons.merge(
        constructors[["constructorId", "name"]], on="constructorId"
    )
    return (
        top_teams_seasons.pivot(index="year", columns="name", values="points")
        .fillna(0)
        .sort_index()
    )


def plot_constructor_points(pivot: pd.DataFrame, output: Optional[Path]) -> None:
    plt.figure(figsize=(14, 7))
    for team_name in pivot.columns:
        plt.plot(pivot.index, pivot[team_name], label=team_name)

    plt.xlabel("Sezon (rok)")
    plt.ylabel("Punkty na koniec sezonu")
    plt.title("Top zespołów F1 – suma punktów na koniec sezonu")
    plt.legend(title="Zespół", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.grid(True)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output, bbox_inches="tight")
    else:
        plt.show()

    plt.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot constructor season standings from Ergast CSV exports.",
    )
    parser.add_argument(
        "--base-dir",
        default=Path("data/main"),
        type=Path,
        help="Directory containing Ergast CSV files (races, constructor_standings, constructors).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save the plot. If omitted, the plot is shown interactively.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top constructors to include in the plot.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    races = load_races(args.base_dir)
    constructor_standings = load_constructor_standings(args.base_dir)
    constructors = load_constructors(args.base_dir)

    pivot = build_constructor_points(races, constructor_standings, constructors, args.top_n)
    plot_constructor_points(pivot, args.output)


if __name__ == "__main__":
    main()
