# Reguły anty-patternów DI (AST check)

Zakres checka: `layers/*` oraz `scrapers/base/*`.

## Co jest traktowane jako naruszenie

1. **Tworzenie zależności typu klient/serwis wewnątrz metod biznesowych**
   - Przykład: `HttpClient()`, `SectionService()`, `WikiFetcher()` w metodzie domenowej typu `process`, `run`, `extract`.
2. **Ukryte składanie zależności poza composition root**
   - Jeżeli metoda nie jest konstruktorem/fabryką (`__init__`, `build*`, `create*`, `factory*`, `compose*`, `wire*`, `setup*`, `configure*`), instancjacja klas o sufiksach `Client|Service|Repository|Adapter|Fetcher` jest raportowana.

## Raportowanie naruszeń

Każde naruszenie zawiera:
- ścieżkę pliku,
- numer linii,
- nazwę klasy i metody,
- nazwę tworzonej zależności,
- sugestię: **wstrzyknij zależność przez `__init__` lub factory (DI)**.

## Wyjątki (tymczasowe)

Dopuszczalne jest oznaczenie pojedynczego miejsca komentarzem:

```python
# di-antipattern-allow: <uzasadnienie>
```

Komentarz działa lokalnie (okno kilku linii przed instancjacją) i powinien być traktowany jako wyjątek przejściowy.

## Powiązanie z ADR

Dla większych zmian (domyślnie: **co najmniej 3 naruszenia** w jednym uruchomieniu checka) CI wymaga referencji `ADR-XXXX` w treści PR (lub commit message dla push).

To mapuje governance na `docs/adr/README.md`, szczególnie wymóg referencji ADR dla większych zmian architektonicznych.
