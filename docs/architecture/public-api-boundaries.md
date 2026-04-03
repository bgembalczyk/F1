# Public API i granice modułów internal

Krótki standard publikowania API pakietów Python w repo.

## 1) `__all__` i re-exporty

- Każdy `__init__.py`, który wystawia publiczne symbole, **musi** mieć jawne `__all__`.
- Re-exporty w `__init__.py` ograniczamy do:
  - stabilnych entrypointów,
  - protokołów/kontraktów używanych między pakietami.
- Nie re-exportujemy „hurtowo” modułów pomocniczych.

## 2) Co jest `internal`

Traktujemy jako `internal`:
- moduły z prefiksem `_` (np. `_registry.py`),
- katalogi techniczne typu `helpers/`, `components/`, `runners/`, o ile ich `__init__.py` nie deklaruje inaczej,
- dowolny moduł nieeksportowany przez `__all__` pakietu nadrzędnego.

## 3) Zakaz deep importów z zewnątrz pakietu

Kod spoza pakietu powinien importować tylko przez publiczne entrypointy:

- ✅ `from layers import create_default_wiki_pipeline_application`
- ✅ `from layers.orchestration import build_layer_one_runner_map`
- ❌ `from layers.orchestration.runners.grand_prix import GrandPrixRunner`

Wyjątki:
- testy jednostkowe konkretnego modułu,
- migracje legacy (czasowe, z ticketem i datą usunięcia).

## 4) Minimalny contract dla nowego pakietu

Nowy pakiet powinien mieć:

1. `__init__.py` z:
   - krótkim opisem publicznego API,
   - `__all__` (nawet jeśli puste).
2. lokalne `README.md` (2–10 punktów):
   - odpowiedzialność katalogu,
   - publiczne entrypointy,
   - czego nie importować z zewnątrz.
