# Architecture Spec

Generated from `scripts/ci/architecture_spec.py`. Do not edit manually.

## layout

### Domains

| Domain | Entrypoint | Layers |
|---|---|---|
| `drivers` | yes | list, sections, infobox, postprocess |
| `constructors` | yes | list, sections, infobox, postprocess |
| `circuits` | yes | list, sections, infobox, postprocess |
| `seasons` | yes | list, sections, postprocess |
| `grands_prix` | yes | list, sections |
| `races` | no | - |
| `engines` | no | - |
| `points` | no | - |
| `sponsorship_liveries` | no | - |
| `tyres` | no | - |

### Shared layers

`list`, `sections`, `infobox`, `postprocess`

## rules

### Forbidden imports by layer

- `list` cannot import: `infobox`, `postprocess`
- `sections` cannot import: `list`, `single_scraper`
- `infobox` cannot import: `list`, `sections`, `postprocess`, `single_scraper`
- `postprocess` cannot import: `list`, `sections`, `infobox`, `single_scraper`

### Allowed imports by layer

- `list` may import: `sections`
- `sections` may import: `infobox`, `postprocess`
- `infobox` may import: -
- `postprocess` may import: -

## deprecation map

### Lifecycle

| Stage | Description |
|---|---|
| `R0` | legacy działa + obowiązkowy DeprecationWarning |
| `R1` | legacy nadal działa + warning pozostaje obowiązkowy |
| `R2` | legacy entrypointy usuwane |

### Legacy module migration

| Old module/command | New module/command | Notes |
|---|---|---|
| `scrapers.circuits.list_scraper` | `scrapers.circuits.entrypoint` | - |
| `scrapers.constructors.current_constructors_list` | `scrapers.constructors.entrypoint` | - |
| `scrapers.drivers.list_scraper` | `scrapers.drivers.entrypoint` | - |
| `scrapers.grands_prix.list_scraper` | `scrapers.grands_prix.entrypoint` | - |
| `scrapers.seasons.list_scraper` | `scrapers.seasons.entrypoint` | - |
| `python main.py --mode <layer0|layer1|full>` | `python -m scrapers.cli wiki --mode <layer0|layer1|full>` | canonical launcher |
