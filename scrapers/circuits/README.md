# Domain pipeline map

## Flow
- `list/` → entrypoints for collection/index pages.
- `sections/` → section-level extraction/parsing for article fragments.
- `infobox/` → infobox normalization/parsing for single entities.
- `postprocess/` → final cleanup/transforms before export.

## Notes
- Keep parser outputs consistent with `SectionParseResult` where section adapters are used.
- Add/update snapshot + alias + contract tests when introducing new parser behavior.


## CLI entrypoint standard
- Moduły uruchamiane bezpośrednio (`python -m ...`) budują launcher przez `build_cli_main(...)` z `scrapers.base.cli_entrypoint`.
- Używaj profili:
  - `list_scraper` dla aktywnych list scraperów,
  - `complete_extractor` dla pełnych ekstraktorów,

- **Rekomendowana ścieżka uruchamiania:** `python -m scrapers.cli ...` (jedyny canonical launcher).
- `entrypoint.py` traktuj jako jedyny wspierany punkt uruchomienia z kodu i CLI.

## Public API
Stabilne importy dla konsumentów:
- `from scrapers.circuits import CircuitsListScraper`
- `from scrapers.circuits import F1SingleCircuitScraper`
- `from scrapers.circuits import F1CompleteCircuitDataExtractor`
- `from scrapers.circuits import export_complete_circuits`

`circuits.helpers` traktuj jako internal.
