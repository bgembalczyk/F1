# Architektura warstw

## Warstwy

- **Domain (`models/`)** – modele domenowe i walidatory wartości.
- **Application (`scrapers/`)** – orkiestracja pobierania, parsowanie HTML i budowanie rekordów domenowych.
- **Infrastructure (`infrastructure/`)** – adaptery do transportu/IO (HTTP, cache, rate‑limiting).

## Zależności między warstwami

- `models/` **nie zna transportu** i nie importuje z `scrapers/` ani `infrastructure/`.
- `scrapers/` może używać modeli z `models/` oraz klientów/adapterów z `infrastructure/`.
- `infrastructure/` nie zależy od `scrapers/` ani `models/` – dostarcza wyłącznie implementacje techniczne.

## Lokalizacja logiki parsowania

- Całe parsowanie HTML i ekstrakcja danych znajduje się w `scrapers/` (np. `scrapers/base/helpers/`, `scrapers/base/table/`, `scrapers/base/infobox/`).
- `infrastructure/` zajmuje się wyłącznie pobieraniem danych i cache, bez logiki parsowania.
