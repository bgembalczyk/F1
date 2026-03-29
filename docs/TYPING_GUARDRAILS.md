# Typing guardrails (rollout etapowy)

## Scope
Aktualny scope bramki typowania (`mypy.ini`):
- `scrapers/base/pipeline_runner.py`
- `scrapers/base/options.py`
- `scrapers/base/table/pipeline.py`
- `scrapers/base/sections/interface.py`
- `layers/`
- `validation/`
- `infrastructure/http_client/`

## Zasady
1. **`Any` poza granicami I/O**
   - dozwolone tylko na styku z niekontrolowanym wejściem/wyjściem (np. surowe JSON/HTTP, serializacja).
   - wewnątrz pipeline i interfejsów domenowych używamy `object`, aliasów domenowych lub `Protocol`.
2. **Brak adnotacji typów zwrotnych w publicznych metodach**
   - publiczna metoda/funkcja (`def name(...)`) musi mieć jawny return type.
3. **Niejawne opcjonalności**
   - `None` musi być jawnie zapisane (`X | None`), bez implicit optional.
4. **Niekompletne adnotacje definicji**
   - wszystkie parametry i return type muszą być typowane.
5. **Nowe moduły: brak `Any` bez uzasadnienia**
   - nowy plik w `layers/`, `validation/`, `infrastructure/http_client/` nie może używać `Any`,
     chyba że obok znajduje się komentarz uzasadniający `ANY-JUSTIFIED:`.

## Rollout etapami (per pakiet)
- **Etap 1 (już aktywny):** `scrapers/base/*` strict, bez wyjątków.
- **Etap 2 (aktywowany):** rozszerzenie `files` o `layers/`, `validation/`,
  `infrastructure/http_client/`.
- **Etap 3 (trwający):** redukcja wyjątków moduł-po-module aż do pełnego strict.

## Lista wyjątków (tymczasowa)
Poniższe moduły mają tymczasowe `ignore_errors = True` w `mypy.ini`:
- `layers.application`
- `layers.one.executor`
- `layers.orchestration.runners.function_export`
- `layers.orchestration.runners.grand_prix`
- `layers.seed.data_classes`
- `layers.seed.helpers`
- `layers.seed.registry.constants`
- `layers.seed.registry.entries`
- `layers.seed.registry.helpers`
- `layers.zero.executor`
- `layers.zero.merge`
- `validation.composite_validator`
- `validation.record_factory_validator`
- `validation.rules`
- `validation.schema_engine`
- `validation.schema_rules`
- `validation.schemas`
- `validation.validator_base`
- `infrastructure.http_client.clients.base`
- `infrastructure.http_client.clients.urllib_http`
- `infrastructure.http_client.components.request_executor`
- `infrastructure.http_client.interfaces.http_client_protocol`
- `infrastructure.http_client.policies.default_retry`
- `infrastructure.http_client.policies.retry`
- `infrastructure.http_client.requests_shim.http_error`
- `infrastructure.http_client.requests_shim.session`

## Bramka regresji CI
CI ma teraz dwie bramki:
1. `enforce_new_module_any_policy.py` — blokuje nowe moduły z `Any` bez `ANY-JUSTIFIED:`.
2. `mypy_regression_gate.py` — porównuje liczbę błędów mypy między `base SHA` i `head SHA`
   i blokuje PR, jeśli liczba błędów wzrośnie.
