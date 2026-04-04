# Coverage backlog (aktualizacja automatyczna)

## Cele fal
- Fala 1 (najwyższy ROI): parsery/helpers + scripts CI z `miss >= 40`; cel: +6–7 pp.
- Fala 2: moduły domenowe i services z `miss 20-39`; cel: +3–4 pp.
- Fala 3: domknięcie wyjątków/fallbacków i niskich plików pojedynczych; cel: +2–3 pp.
- Fala 4: polerka do 99% – pojedyncze linie i granice warunków; cel: +1–2 pp.

## Fala 1
- [ ] `scripts/ci/enforce_structural_quality.py` — miss: 96, coverage: 46.96%
- [ ] `scrapers/seasons/parsers/entry_merger.py` — miss: 89, coverage: 53.89%
- [ ] `scripts/ci/enforce_diff_quality_guards.py` — miss: 80, coverage: 47.02%
- [ ] `scrapers/drivers/infobox/parsers/general.py` — miss: 76, coverage: 47.95%
- [ ] `scrapers/drivers/infobox/parsers/link_extractor.py` — miss: 72, coverage: 44.62%
- [ ] `scrapers/drivers/infobox/parsers/best_finish.py` — miss: 70, coverage: 53.33%
- [ ] `scrapers/seasons/columns/helpers/race_result/cell_parser.py` — miss: 70, coverage: 30.69%
- [ ] `scrapers/base/table/columns/helpers/constructor_parsing.py` — miss: 68, coverage: 32.67%
- [ ] `scrapers/base/table/columns/helpers/results_parsing.py` — miss: 68, coverage: 34.62%
- [ ] `scrapers/base/table/parser.py` — miss: 61, coverage: 66.11%
- [ ] `scrapers/points/parsers.py` — miss: 61, coverage: 62.8%
- [ ] `scrapers/drivers/infobox/parsers/collapsible_table.py` — miss: 59, coverage: 3.28%
- [ ] `scrapers/sponsorship_liveries/parsers/splitters/record/strategies/season.py` — miss: 58, coverage: 38.3%
- [ ] `scrapers/sponsorship_liveries/parsers/section.py` — miss: 57, coverage: 66.27%

## Fala 2
- Brak plików w top N.

## Fala 3
- [ ] `scrapers/circuits/models/services/lap_record_merging.py` — miss: 207, coverage: 42.98%
- [ ] `layers/zero/merge.py` — miss: 156, coverage: 64.38%
- [ ] `scrapers/sponsorship_liveries/columns/sponsor.py` — miss: 132, coverage: 49.43%
- [ ] `scrapers/engines/engine_manufacturers_list.py` — miss: 116, coverage: 29.7%
- [ ] `scrapers/constructors/constructors_list.py` — miss: 97, coverage: 40.85%
- [ ] `scrapers/grands_prix/red_flagged_races_scraper/combined.py` — miss: 91, coverage: 63.75%
- [ ] `scrapers/seasons/columns/race_result.py` — miss: 89, coverage: 25.83%
- [ ] `scrapers/circuits/models/services/normalization.py` — miss: 85, coverage: 50.58%
- [ ] `scrapers/base/abc.py` — miss: 80, coverage: 59.8%
- [ ] `scripts/check_di_antipatterns.py` — miss: 70, coverage: 51.39%
- [ ] `scripts/check_architecture_rules.py` — miss: 69, coverage: 31.68%
- [ ] `scrapers/engines/engine_restrictions.py` — miss: 68, coverage: 33.98%
- [ ] `scrapers/circuits/infobox/services/specs.py` — miss: 64, coverage: 49.21%
- [ ] `scrapers/base/table/columns/types/links_list.py` — miss: 58, coverage: 25.64%
- [ ] `layers/zero/executor.py` — miss: 55, coverage: 51.33%
- [ ] `scrapers/base/scraper_components.py` — miss: 55, coverage: 71.05%

## Fala 4
- Brak plików w top N.
