# Scrapers package migration map

## Target contract

- `scrapers/core/*`: abstraction and base classes (`options`, `run_config`, `errors`, and core families for `table/*`, `infobox/*`, `orchestration/*`).
- `scrapers/domain/<domain>/*`: domain implementations and exports.
- `scrapers/legacy/*`: deprecated compatibility aliases only.

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

## L0/L1 critical path migration status

1. `layers/orchestration/*`: imports redirected to `scrapers.core.*` and `scrapers.domain.exports`.
2. `layers/executors/*`: imports redirected to `scrapers.core.*`.
3. `wiki_pipeline/*`: run-config imports redirected to `scrapers.core.run_config`.
4. `complete_extractor/*`: base imports redirected to `scrapers.core.*`.
