# config/

Centralny mechanizm konfiguracji aplikacji oparty o `AppConfigProvider` (`config/app_config_provider.py`).

## Jedno źródło prawdy

Od teraz komponenty (np. klient Gemini, helpery HTTP, scrapery) **nie powinny** robić lokalnych/ad-hoc odczytów konfiguracji. Zamiast tego korzystają z:

```python
from config.app_config_provider import AppConfigProvider

app_config = AppConfigProvider().get()
```

## Źródła konfiguracji i priorytety

Konfiguracja jest rozwiązywana w kolejności:

1. **Zmienne środowiskowe** (najwyższy priorytet).
2. **Pliki lokalne** (fallback, gdy brak wartości w env).
3. **Wartości domyślne w kodzie** (najniższy priorytet).

## Obsługiwane ustawienia

### Tryb aplikacji
- `APP_MODE` (domyślnie: `development`).

### Ścieżki
- `APP_CONFIG_DIR` (domyślnie: `<repo>/config`).
- `APP_DATA_DIR` (domyślnie: `<repo>/data`).
- `GEMINI_API_KEY_FILE` (domyślnie: `<config_dir>/gemini_api_key.txt`).

### Gemini
- `GEMINI_API_KEY` (jeśli ustawione, ma pierwszeństwo nad plikiem).
- `GEMINI_TIMEOUT_SECONDS` (domyślnie: `30`).

### HTTP
- `HTTP_TIMEOUT_SECONDS` (domyślnie: timeout z `infrastructure.http_client.policies.constants`).

## Klucz Gemini API

Jeżeli nie używasz `GEMINI_API_KEY` w env, utwórz plik `config/gemini_api_key.txt` i wpisz klucz:

```
AIza...twoj_klucz...
```

Plik jest wykluczony z repozytorium przez `.gitignore`.
Klucz można wygenerować na: https://aistudio.google.com/app/apikey
