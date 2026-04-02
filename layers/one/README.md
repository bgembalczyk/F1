# layers/one

## Odpowiedzialność
Warstwa 1 odpowiada za uruchamianie scrape'ów typu „complete” dla seedów z registry, delegację wykonania do runnerów domenowych oraz uruchomienie kroku końcowego dla engine manufacturers.

## Punkt wejścia
- Publiczny alias: `LayerOneRunner` (`layers.one.__init__`).
- Główny kontrakt uruchomienia: `LayerOneExecutor.run(run_config, base_wiki_dir)`.

## Najczęstszy punkt debug
Najczęściej debug zaczyna się w `layers/one/executor.py`, w szczególności przy:
- budowie `runner_map`,
- mapowaniu `seed_name -> runner`,
- obsłudze przypadków `runner is None`.

Drugi typowy punkt to implementacje runnerów w `layers/orchestration/runners/*`, gdy seed przechodzi przez executor, ale nie daje oczekiwanego outputu.

## Czego tu nie robić
- Nie osadzać tu logiki HTTP/fetch i niskopoziomowych retry (to odpowiedzialność infrastruktury/scraperów).
- Nie wrzucać tu transformacji rekordów „na skróty” zamiast do pipeline scrapera.
- Nie dokładać specjalnych wyjątków per seed bez aktualizacji `runner_map` i jawnego kontraktu runnera.
- Nie traktować tego modułu jako miejsca do globalnych side-effectów niezwiązanych z wykonaniem layer 1.
