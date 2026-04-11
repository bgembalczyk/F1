# Scrapers import migration map

## Status

Migracja importów zakończona. Nie utrzymujemy już aliasowych modułów przejściowych ani instrukcji tymczasowych.

## Canonical imports

- `scrapers.wiring.factory`
- `scrapers.wiring.runtime.factory`
- `scrapers.wiring.composition_drivers`
- `scrapers.wiring.composition_seasons`
- `scrapers.contracts.protocols_wiki`
- `scrapers.contracts.protocols`
- `scrapers.contracts.protocols.data_frame_formatter`
- `scrapers.contracts.protocols.fieldnames_strategy`
- `scrapers.contracts.protocols.has_table_parser`

## Layering rule

`contracts/` contains only Protocol/ABC-style contracts and must not import `implementations/` classes.
