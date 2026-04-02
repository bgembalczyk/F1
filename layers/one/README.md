# layers/one

## Cel modułu
Warstwa 1 uruchamia scrape'y „complete” dla seedów z registry, delegując wykonanie do runnerów domenowych i finalnie odpala dodatkowy krok dla engine manufacturers.

## Główne klasy
- `LayerOneExecutor` – orkiestracja pętli po `seed_registry`.
- `LayerJobRunner` (ABC) – kontrakt dla runnerów warstwy 1.
- Przykładowy runner: `GrandPrixRunner`.

## Co jest publiczne
- Publiczny alias: `LayerOneRunner` (alias do `LayerOneExecutor`) z `layers.one.__init__`.
- Publiczny kontrakt uruchomienia: `LayerOneExecutor.run(run_config, base_wiki_dir)`.

## Gdzie najczęściej debugować
- `layers/one/executor.py`: budowanie `runner_map`, obsługa seedów bez wsparcia (`runner is None`).
- `layers/orchestration/runners/*`: implementacje konkretnych runnerów i ich output paths.
- Logi kontekstowe (`run_id`, `seed_name`, `domain`) emitowane podczas pętli.

## Najczęstsze pułapki
- Brak runnera dla `seed_name` nie rzuca wyjątku — seed jest tylko pomijany z warningiem.
- Niespójność między `seed_registry` i `runner_map` daje „ciche” braki w danych.
- Łatwo przeoczyć, że `engine_manufacturers_runner` uruchamia się zawsze po pętli seedów.
