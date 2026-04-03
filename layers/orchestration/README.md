# layers/orchestration — README techniczne

## Odpowiedzialność
- Budowa map uruchamiania warstwy 0/1.
- Definicja kontraktów runnerów/factory dla orchestration.

## Public API
- `layers.orchestration.build_layer_one_runner_map`
- `layers.orchestration.build_layer_zero_run_config_factory_map`
- `layers.orchestration.run_engine_manufacturers`

## Co jest internal
- `layers/orchestration/runners/*` — implementacje runnerów.
- `layers/orchestration/factories.py` — szczegóły budowy kwargs/config.

## Zasady importu
- Kod spoza pakietu importuje przez `layers.orchestration` (nie przez `runners/*`).
- Re-exporty utrzymujemy jawnie przez `__all__`.
