# Scrapers package migration map

## Status

Migracja została zakończona: kod i testy używają modułów kanonicznych, a wrappery kompatybilności zostały usunięte.

## Target contract

- `scrapers/core/*`: abstraction and base classes (`options`, `run_config`, `errors`, and core families for `table/*`, `infobox/*`, `orchestration/*`).
- `scrapers/domain/<domain>/*`: domain implementations and exports.
- Brak warstwy `scrapers/legacy/*` dla nowych zmian.

## Module map (key families)

- `scrapers.options` -> `scrapers.core.options`
- `scrapers.run_config` -> `scrapers.core.run_config`
- `scrapers.errors` -> `scrapers.core.errors`
- `scrapers.orchestration.*` -> `scrapers.core.orchestration.*`
- `scrapers.infobox.*` -> `scrapers.core.infobox.*`
- `scrapers.*table*` modules -> `scrapers.core.table.*`
- Domain export helpers used by orchestration:
  - `complete_extractor.export.*` + `scrapers.helpers_seasons.export_complete_seasons`
  - canonicalized via `scrapers.domain.exports`
