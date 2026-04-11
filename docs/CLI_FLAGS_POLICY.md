# RunConfig / IDE entrypoint — polityka stabilnego API uruchomień

## 1) Stabilny kontrakt uruchomień

Stabilnym kontraktem uruchomień jest funkcja startowa domeny:

- `scrapers.<domain>.entrypoint.run_list_scraper(...)`

To jest kontrakt utrzymywany dla integracji kodowych (IDE, testy architektoniczne, import bezpośredni).

## 2) Profile `RunConfig`

Profile runtime są scentralizowane w `scrapers.base.run_profiles`:

- `default` (domyślny)
- `debug` (opcjonalny profil diagnostyczny)

To zastępuje wcześniejsze rozdrobnienie (`strict` / `minimal` / `deprecated`) i zamyka temat profili przejściowych.

## 3) Polityka redukcji opcji

- Usuwamy opcje rzadko używane i duplikujące się semantycznie.
- Każdy nowy profil musi uzasadniać różnicę względem `default`; w przeciwnym razie nie powstaje.
- Jedynym kontraktem uruchomieniowym jest aktualny interfejs CLI i entrypointy kanoniczne; nie utrzymujemy wrapperów przejściowych.

## 4) Wymuszenie YAGNI dla nowych opcji runtime

Nowe opcje runtime muszą być deklarowane w katalogu `CliFlagSpec` i zawierać:

- `justification` (po co opcja istnieje),
- `review_by` (termin przeglądu, czy opcja nadal jest potrzebna).

Walidacja katalogu opcji traktuje brak któregokolwiek pola jako błąd konfiguracji.
