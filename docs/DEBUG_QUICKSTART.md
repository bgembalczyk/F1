# DEBUG QUICKSTART (15 minut)

Cel: w 15 minut zawęzić źródło problemu do konkretnej warstwy i modułu (`CLI -> Layer 0 -> Layer 1`).

> Ten dokument jest „pierwszym wejściem” do debugowania. Szersze scenariusze znajdziesz w `docs/DEBUG_COOKBOOK.md`.

---

## Plan 15-minutowy

## 0:00-2:00 — Potwierdź punkt wejścia i tryb uruchomienia

1. Zweryfikuj komendę uruchomienia (`python -m scrapers.cli ...`) i argumenty (`--mode`, profil, domena).
2. Sprawdź, czy log startowy pokazuje oczekiwany moduł oraz seedy.

**Gdzie wejść w kod:**
- `scrapers/cli.py`
- `layers/application.py`
- `layers/pipeline.py`

---

## 2:00-6:00 — Prześledź flow Layer 0 (raw -> merge)

1. Sprawdź, czy joby Layer 0 faktycznie ruszyły i zakończyły się sukcesem.
2. Potwierdź obecność plików `raw`.
3. Jeśli `raw` istnieje, sprawdź merge domeny (`<domain>.json`).

**Flow do prześledzenia:**
- `layers/zero/executor.py` (uruchomienie jobów, ścieżki output)
- `layers/zero/merge.py` (deduplikacja, transformery, zapis merged)

**Pliki wynikowe do sprawdzenia:**
- `layers/0_layer/<domain>/raw/*.json`
- `layers/0_layer/<domain>/<domain>.json`

---

## 6:00-10:00 — Prześledź flow Layer 1 (complete)

1. Zweryfikuj, czy seed nie jest pomijany (`unsupported seed`).
2. Potwierdź, że runner dla seeda istnieje i jest mapowany.
3. Sprawdź, czy finalny output został zapisany.

**Gdzie wejść w kod:**
- `layers/one/executor.py`
- `layers/orchestration/runner_registry.py`
- `layers/orchestration/runners/*.py`

**Pliki wynikowe do sprawdzenia:**
- `layers/1_layer/complete/*.json` (lub katalog wynikowy wskazany przez konfigurację)

---

## 10:00-15:00 — Izolacja i szybka hipoteza

1. Weź 1 rekord problematyczny i porównaj: `raw -> merged -> complete`.
2. Jeśli rekord znika między etapami, zawęź problem do konkretnej funkcji w warstwie.
3. Sprawdź mapowanie transformera (`domain + source_name`) i reguły merge.

**Najczęściej kluczowe miejsca:**
- `layers/zero/merge.py` (`TRANSFORM_PIPELINES`, dobór handlera, logika merge)
- `layers/one/executor.py` (mapowanie seed -> runner)

---

## Mapa: objaw -> prawdopodobne miejsce w kodzie

| Objaw | Prawdopodobne miejsce | Co sprawdzić najpierw |
|---|---|---|
| Brak rekordu w output końcowym | `layers/zero/merge.py`, `layers/one/executor.py` | Czy rekord jest w `raw`; czy przechodzi do merged; czy seed ma runner |
| Brak jakichkolwiek plików `raw` | `scrapers/cli.py`, `layers/zero/executor.py` | Czy uruchamiasz poprawny moduł/tryb; czy katalog output jest poprawny |
| Duplikaty rekordów | `layers/zero/merge.py` | Klucz deduplikacji, aliasy nazw, łączenie wielu źródeł |
| Rekord ma złą strukturę pól | `layers/zero/merge.py` | Jaki transformer został dobrany po `domain + source_name` |
| Log: `skipping unsupported seed` | `layers/one/executor.py`, `layers/orchestration/runner_registry.py` | Spójność nazwy seeda i mapowania runnerów |
| Pipeline kończy się „sukcesem”, ale brak complete output | `layers/one/executor.py`, konfiguracja ścieżek | Czy zapis idzie do oczekiwanego katalogu i profilu |

---

## Definition of Done (zmiany architektoniczne)

Dla każdej zmiany architektonicznej dotyczącej przepływu `CLI/Layer0/Layer1`:

- [ ] Zaktualizowano ten dokument (`docs/DEBUG_QUICKSTART.md`), jeśli zmieniły się:
  - punkty wejścia,
  - flow wykonania,
  - ścieżki plików wynikowych,
  - mapa „objaw -> miejsce w kodzie”.
- [ ] W opisie PR dodano krótką notkę: **„Debug Quickstart updated: yes/no + uzasadnienie”**.
- [ ] Jeśli update nie był potrzebny, w PR podano powód (np. „zmiana wyłącznie lokalna, bez wpływu na flow”).

To traktujemy jako stały element DoD dla zmian architektonicznych.
