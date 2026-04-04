# Polityka jakości coverage (CI)

Ten dokument opisuje obowiązujące bramki coverage uruchamiane w CI.

## 1) Patch coverage: brak spadku dla zmienionych plików

Dla każdego zmienionego pliku Python (`git diff base..head`) CI porównuje coverage pliku względem baseline (`.ci/coverage-baseline.json`).

Reguła:
- coverage pliku **nie może spaść** względem baseline.

## 2) Globalny próg coverage – stopniowo rosnący

Globalny próg coverage jest zdefiniowany jako ścieżka:

- `85 → 88 → 91 → 94 → 97 → 99`

Konfiguracja:
- `.ci/coverage-policy.json` (`global_threshold_path`, `current_sprint`).

Reguła:
- coverage globalne z bieżącego runu (`coverage.xml`) musi być >= progu dla `current_sprint`.

## 3) Minimalny przyrost globalny na sprint

Wymagany minimalny przyrost globalnego progu coverage na sprint to domyślnie:

- `+1.5 pp`

Konfiguracja:
- `.ci/coverage-policy.json` (`minimum_global_increment_per_sprint_pp`).

Reguła:
- każda para kolejnych progów na ścieżce `global_threshold_path` musi mieć różnicę >= `minimum_global_increment_per_sprint_pp`.

## 4) Legacy low coverage: obowiązkowa poprawa przy dotknięciu

Pliki legacy o niskim coverage są utrzymywane jawnie:

- `.ci/legacy-low-coverage-files.txt`

Reguła:
- gdy plik z listy `legacy low coverage` jest zmieniony, coverage tego pliku musi wzrosnąć o co najmniej `legacy_minimum_improvement_pp` (domyślnie `+0.5 pp`) względem baseline.

## 5) Egzekucja reguł w pipeline CI

Pipeline:
- Workflow: `.github/workflows/test-profiles.yml`
- Krok: `Coverage quality gates (patch/global/legacy)`
- Skrypt: `scripts/ci/enforce_coverage_quality.py`

Skrypt wymaga:
- raportu coverage XML (`coverage.xml`),
- policy (`.ci/coverage-policy.json`),
- baseline (`.ci/coverage-baseline.json`),
- listy plików legacy (`.ci/legacy-low-coverage-files.txt`),
- SHA bazowego i docelowego commita (dla listy zmienionych plików).
