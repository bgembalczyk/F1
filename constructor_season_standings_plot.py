import pandas as pd
import matplotlib.pyplot as plt

# Wczytanie danych
src_races = pd.read_csv("data/main/races.csv")
src_constructors_standings = pd.read_csv("data/main/constructor_standings.csv")
src_constructors = pd.read_csv("data/main/constructors.csv")

races = src_races[["raceId", "year"]].copy()
constructors_standings = src_constructors_standings[
    ["constructorStandingsId", "raceId", "constructorId", "points"]
].copy()
constructors = src_constructors[["constructorId", "name"]].copy()

df = constructors_standings.copy()

df = pd.merge(df, races, on="raceId", how="left").merge(
    constructors, on="constructorId", how="left"
)

# Sumowanie punktów końcowych w sezonach (maksymalna wartość dla danego zespołu i sezonu)
season_points = df.groupby(["year", "constructorId"])["points"].max().reset_index()

# Sumowanie całkowitej liczby punktów w historii
total_points = season_points.groupby("constructorId")["points"].sum().reset_index()

# Dodanie nazw zespołów
total_points = total_points.merge(
    constructors[["constructorId", "name"]], on="constructorId"
)

# Wybór top 10 zespołów
top_10 = total_points.sort_values("points", ascending=False).head(10)
top_ids = top_10["constructorId"]

# Filtrowanie danych tylko dla top 10
top_teams = season_points[season_points["constructorId"].isin(top_ids)]

# Dodanie nazw do sezonowych danych
top_teams = top_teams.merge(constructors[["constructorId", "name"]], on="constructorId")

# Pivot: rok jako wiersze, kolumny = nazwy zespołów, wartości = punkty
pivot = top_teams.pivot(index="year", columns="name", values="points").fillna(0)

# Rysowanie wykresu
plt.figure(figsize=(14, 7))
for team_name in pivot.columns:
    plt.plot(pivot.index, pivot[team_name], label=team_name)

plt.xlabel("Sezon (rok)")
plt.ylabel("Punkty na koniec sezonu")
plt.title("Top 10 zespołów F1 – suma punktów na koniec sezonu")
plt.legend(title="Zespół", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.grid(True)
plt.show()
