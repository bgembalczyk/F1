# infrastructure/http_client/components — README techniczne

## Odpowiedzialność
- Komponenty composable do wykonywania zapytań HTTP i cache odpowiedzi.

## Publiczne API
- `HeaderResolver`
- `RequestExecutor`
- `ResponseCacheService`

Publiczne symbole są eksportowane przez `infrastructure.http_client.components.__all__`.

## Granice
- Moduły w tym katalogu są niskopoziomowe; wyższe warstwy powinny preferować fabryki/polityki z `infrastructure.http_client`.
