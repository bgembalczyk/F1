# RunConfig / IDE entrypoint — polityka stabilnego API uruchomień

## 1) Stabilny kontrakt uruchomień

Stabilnym kontraktem uruchomień jest funkcja startowa domeny:

- `scrapers.<domain>.entrypoint.run_list_scraper(...)`

To jest kontrakt utrzymywany dla integracji kodowych (IDE, testy architektoniczne, import bezpośredni).

## 2) Profile `RunConfig`

Profile runtime są scentralizowane w `scrapers.base.run_profiles`:

- `default` (domyślny)
- `debug` (opcjonalny profil diagnostyczny)

To zastępuje wcześniejsze rozdrobnienie (`strict` / `minimal` / `deprecated`) mapowane teraz do jednego zachowania domyślnego.

## 3) Polityka redukcji opcji

- Usuwamy opcje rzadko używane i duplikujące się semantycznie.
- Każdy nowy profil musi uzasadniać różnicę względem `default`; w przeciwnym razie nie powstaje.
- Kompatybilność terminalowa (`python -m ...`, legacy CLI wrappery) nie jest już traktowana jako kontrakt obowiązkowy.

## 4) Wymuszenie YAGNI dla nowych opcji runtime

Nowe opcje runtime muszą być deklarowane w katalogu `CliFlagSpec` i zawierać:

- `justification` (po co opcja istnieje),
- `review_by` (termin przeglądu, czy opcja nadal jest potrzebna).

Walidacja katalogu opcji traktuje brak któregokolwiek pola jako błąd konfiguracji.
