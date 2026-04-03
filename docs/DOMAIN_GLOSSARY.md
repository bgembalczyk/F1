# Domain glossary (canonical terminology)

Dokument definiuje **kanoniczne** nazwy używane w modelach domenowych, transformacjach i identyfikatorach rekordów.

## Canonical terms + forbidden synonyms

| Obszar | Canonical term | Niedozwolone warianty (synonimy/legacy) |
|---|---|---|
| Record identifier | `grands_prix` | `grand_prix`, `grandprix`, `gp` |
| Driver fields | `race_entries` | `entries` |
| Driver fields | `race_starts` | `starts` |
| Driver fields | `pole_positions` | `poles` |
| Constructor fields | `wcc_titles` | `wcc` |
| Constructor fields | `wdc_titles` | `wdc` |
| Grand Prix fields | `race_title` | `title`, `gp_title` |
| Grand Prix fields | `race_status` | `status`, `gp_status` |
| Grand Prix fields | `years_held` | `years`, `seasons` |

## Machine-readable map for CI

Każda linia ma format: `forbidden -> canonical`.

```text
grandprix -> grands_prix
gp_title -> race_title
gp_status -> race_status
```

## Rule

W nowych zmianach należy używać wyłącznie canonical terms. Legacy warianty mogą być obsłużone tylko jako alias wejściowy w warstwie transformacji.
