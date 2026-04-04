# Coverage Priorytetyzacja (na bazie `.coverage`)
- Bazowy global coverage (aproksymacja AST): **82.83%** (30274/36549)
- Reguła fal: Fala 1 `miss >= 40`, Fala 2 `20-39`, Fala 3 `<20`.

## Tabela priorytetów – ROI starter
| file | miss | cover | kategoria | fala | cel odzysku (linie) | oczekiwany nowy % globalny* |
|---|---:|---:|---|---|---:|---:|
| `scrapers/circuits/models/services/lap_record_merging.py` | 154 | 57.58% | scraper | Fala 1 | 154 | 83.25% |
| `scripts/ci/enforce_structural_quality.py` | 96 | 46.96% | scripts | Fala 1 | 96 | 83.52% |
| `scrapers/seasons/columns/race_result.py` | 78 | 35.00% | scraper | Fala 1 | 78 | 83.73% |
| `scrapers/base/table/columns/helpers/constructor_parsing.py` | 68 | 32.67% | scraper | Fala 1 | 68 | 83.91% |
| `scrapers/base/table/columns/helpers/results_parsing.py` | 62 | 40.38% | scraper | Fala 1 | 62 | 84.08% |
| `scripts/ci/enforce_diff_quality_guards.py` | 61 | 59.60% | scripts | Fala 1 | 61 | 84.25% |
| `scripts/check_architecture_rules.py` | 52 | 48.51% | scripts | Fala 1 | 52 | 84.39% |
| `scripts/check_di_antipatterns.py` | 46 | 68.06% | scripts | Fala 1 | 46 | 84.52% |
| `scripts/ci/enforce_function_complexity.py` | 35 | 60.23% | scripts | Fala 2 | 35 | 84.62% |
| `scripts/check_domain_terminology.py` | 21 | 58.00% | scripts | Fala 2 | 21 | 84.67% |

\* kolumna liczona kumulacyjnie po kolei z tabeli (malejąco po `miss`).

## Fale – podsumowanie całości
| fala | liczba plików | suma miss |
|---|---:|---:|
| Fala 1 | 31 | 2036 |
| Fala 2 | 58 | 1539 |
| Fala 3 | 853 | 2700 |

## Top 25 globalnie (malejąco po `miss`)
| file | miss | cover | kategoria | fala |
|---|---:|---:|---|---|
| `scrapers/circuits/models/services/lap_record_merging.py` | 154 | 57.58% | scraper | Fala 1 |
| `scrapers/sponsorship_liveries/columns/sponsor.py` | 121 | 53.64% | scraper | Fala 1 |
| `scrapers/engines/engine_manufacturers_list.py` | 105 | 36.36% | scraper | Fala 1 |
| `scripts/ci/enforce_structural_quality.py` | 96 | 46.96% | scripts | Fala 1 |
| `scrapers/constructors/constructors_list.py` | 89 | 45.73% | scraper | Fala 1 |
| `scrapers/grands_prix/red_flagged_races_scraper/combined.py` | 85 | 66.14% | scraper | Fala 1 |
| `scrapers/seasons/columns/race_result.py` | 78 | 35.00% | scraper | Fala 1 |
| `tests/test_scraper_errors.py` | 77 | 60.91% | tests-support | Fala 1 |
| `scrapers/seasons/parsers/entry_merger.py` | 75 | 61.14% | scraper | Fala 1 |
| `scrapers/seasons/columns/helpers/race_result/cell_parser.py` | 70 | 30.69% | scraper | Fala 1 |
| `tests/test_record_factories_snapshot_compat.py` | 69 | 18.82% | tests-support | Fala 1 |
| `scrapers/base/table/columns/helpers/constructor_parsing.py` | 68 | 32.67% | scraper | Fala 1 |
| `scrapers/base/table/columns/helpers/results_parsing.py` | 62 | 40.38% | scraper | Fala 1 |
| `scripts/ci/enforce_diff_quality_guards.py` | 61 | 59.60% | scripts | Fala 1 |
| `scrapers/drivers/infobox/parsers/link_extractor.py` | 59 | 54.62% | scraper | Fala 1 |
| `scrapers/engines/engine_restrictions.py` | 55 | 46.60% | scraper | Fala 1 |
| `layers/zero/merge.py` | 53 | 87.90% | domain | Fala 1 |
| `scrapers/base/table/columns/types/links_list.py` | 53 | 32.05% | scraper | Fala 1 |
| `scrapers/circuits/models/services/normalization.py` | 52 | 69.77% | scraper | Fala 1 |
| `scripts/check_architecture_rules.py` | 52 | 48.51% | scripts | Fala 1 |
| `scrapers/circuits/infobox/services/specs.py` | 50 | 60.32% | scraper | Fala 1 |
| `scrapers/drivers/infobox/parsers/collapsible_table.py` | 49 | 19.67% | scraper | Fala 1 |
| `scrapers/base/abc.py` | 48 | 75.88% | scraper | Fala 1 |
| `scrapers/drivers/infobox/parsers/general.py` | 48 | 67.12% | scraper | Fala 1 |
| `scrapers/sponsorship_liveries/parsers/splitters/record/strategies/season.py` | 48 | 48.94% | scraper | Fala 1 |
