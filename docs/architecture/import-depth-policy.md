# Audyt głębokości modułów i polityka importów

## 1) Pakiety o największej głębokości ścieżek

Na podstawie przeglądu `scrapers/*` i `layers/*` najwyższą głębokość miały:

- `scrapers/seasons/columns/helpers/race_result/rules/round/*` (głębokość plików: 8 segmentów).
- `scrapers/sponsorship_liveries/parsers/splitters/record/strategies/*` (głębokość plików: 7 segmentów).
- `layers/seed/registry/*` oraz `layers/orchestration/runners/*` (głębokość plików: 4 segmenty).

## 2) Konsolidacja drobnych podmodułów

Skonsolidowano drobne elementy reguł rundy z:

- `.../rules/round/context.py`
- `.../rules/round/protocol.py`
- `.../rules/round/half_points.py`
- `.../rules/round/double_points.py`

Do jednego modułu:

- `scrapers/seasons/columns/helpers/race_result/rules/round_rules.py`

Nowy moduł zawiera pełną odpowiedzialność domenową dla reguł rundy (kontekst + protokół + implementacje).

## 3) Zasada maksymalnej głębokości importu

Wprowadzono zasadę dla nowego kodu:

- Maksymalna głębokość importu dla modułów z `scrapers.*` i `layers.*` to **7 segmentów**.
- Reguła jest egzekwowana testem architektonicznym `tests/test_import_depth_policy.py`.

Przykład:

- ✅ `scrapers.seasons.columns.helpers.race_result.rules.round_rules` (7)
- ❌ import z 8+ segmentami

## 4) Aliasy przejściowe (bez nagłego breaking change)

Pozostawiono kompatybilność wsteczną przez aliasy w starym pakiecie `.../rules/round/*`.

Stare ścieżki importów nadal działają i re-eksportują symbole z `round_rules.py`.
