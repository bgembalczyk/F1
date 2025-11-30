import pandas as pd

# Wczytanie danych
src_results = pd.read_csv("data/main/results.csv")
src_races = pd.read_csv("data/main/races.csv")
src_circuits = pd.read_csv("data/main/circuits.csv")
src_drivers = pd.read_csv("data/main/drivers.csv")
src_constructors = pd.read_csv("data/main/constructors.csv")

circuits = src_circuits[["circuitId", "name"]]
races = src_races[["raceId", "circuitId"]]
results = src_results[["raceId", "driverId", "constructorId", "positionOrder"]]
drivers = src_drivers[["driverId", "forename", "surname"]]
constructors = src_constructors[["constructorId", "name"]]

data = (
    results.merge(races, on="raceId", how="left")
    .merge(drivers, on="driverId", how="left")
    .merge(constructors, on="constructorId", how="left")
    .merge(circuits, on="circuitId", how="left", suffixes=("", "_circuit"))
)

winners = data[data["positionOrder"] == 1]

# Zliczanie zwycięstw na torach
circuit_wins = (
    winners.groupby(["circuitId", "name_circuit", "driverId", "forename", "surname"])
    .size()
    .reset_index(name="wins")
)
# Sortowanie według liczby zwycięstw
circuit_wins = circuit_wins.sort_values(by="wins", ascending=False)
# Zapisanie wyników do pliku CSV
circuit_wins.to_csv("data/circuits_wins.csv", index=False)
# Wyświetlenie wyników
print(circuit_wins.head(10))  # Wyświetlenie 10 torów z największą liczbą zwycięstw
