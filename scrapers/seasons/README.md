# Domain pipeline map

## Flow
- `list/` → entrypoints for collection/index pages.
- `sections/` → section-level extraction/parsing for article fragments.
- `infobox/` → infobox normalization/parsing for single entities.
- `postprocess/` → final cleanup/transforms before export.

## Notes
- Keep parser outputs consistent with `SectionParseResult` where section adapters are used.
- Add/update snapshot + alias + contract tests when introducing new parser behavior.


## IDE entrypoint standard (PyCharm Run)
- Jedyny wspierany sposób uruchamiania to konfiguracja **Run** w **PyCharm**.
- Uruchamianie modułów z terminala (`python -m ...`, w tym `python -m scrapers.cli ...`) jest niewspierane.
- `entrypoint.py` traktuj jako API do wywołań z kodu i docelowy punkt startu dla konfiguracji Run.
- Moduły typu `list_scraper.py`/`complete_scraper.py` pozostają wyłącznie warstwą kompatybilnościową i deprecated.

## Public API
Stabilne importy dla konsumentów:
- `from scrapers.seasons import SeasonsListScraper`
- `from scrapers.seasons import SingleSeasonScraper`
- `from scrapers.seasons import CompleteSeasonDataExtractor`
- `from scrapers.seasons import export_complete_seasons`

`seasons.helpers` traktuj jako internal.
