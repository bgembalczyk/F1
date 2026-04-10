# Scrapers import migration map

## Transition period

Backward-compatible alias modules are kept to support migration. They emit `DeprecationWarning` on import.

## Old -> new imports

- `scrapers.factory` -> `scrapers.wiring.factory`
- `scrapers.runtime.factory` -> `scrapers.wiring.runtime.factory`
- `scrapers.composition_drivers` -> `scrapers.wiring.composition_drivers`
- `scrapers.composition_seasons` -> `scrapers.wiring.composition_seasons`
- `scrapers.protocols_wiki` -> `scrapers.contracts.protocols_wiki`
- `scrapers.protocols` -> `scrapers.contracts.protocols`
- `scrapers.protocols.data_frame_formatter` -> `scrapers.contracts.protocols.data_frame_formatter`
- `scrapers.protocols.fieldnames_strategy` -> `scrapers.contracts.protocols.fieldnames_strategy`
- `scrapers.protocols.has_table_parser` -> `scrapers.contracts.protocols.has_table_parser`

## Layering rule

`contracts/` contains only Protocol/ABC-style contracts and must not import `implementations/` classes.
