# Przyszła wizja aplikacji: F1 Wiki → Datasety ML

## Cel produktu
Aplikacja ma budować wysokiej jakości datasety pod machine learning, zaczynając od publicznie dostępnych danych z Wikipedii i docelowo wzbogacając je danymi z dedykowanych API.

## Założenia architektoniczne
- Główny fundament: **architektura oparta o wiki-parsery**.
- Przetwarzanie opiera się na **dwóch warstwach roboczych (0 i 1)**, które wykonujemy iteracyjnie.
- Każde przejście zapisuje wyniki jako ustrukturyzowane JSON-y podzielone kategoriami.
- Wyniki jednego przejścia stają się wejściem do kolejnego przejścia.
- Zakres i kolejność przejść są sterowane **na sztywno w kodzie** (bez pełnego automatycznego recrawla).
- Za każdym przejściem musi być jawnie wskazane: **z którego pliku/kategorii bierzemy kolejne punkty startowe**.

## Punkty startowe (seed pages)
W pierwszej fazie skupiamy się na Formule 1 i stronach listowych Wikipedii:
- lista kierowców F1,
- lista konstruktorów F1,
- lista Grand Prix,
- lista torów,
- lista sezonów,
- ewentualnie: lista silników, dostawców opon, team principals, rekordów.

Każdy punkt startowy powinien mieć:
1. Zdefiniowany scraper strony,
2. Zdefiniowany parser tabel/list,
3. Zmapowany schemat rekordu wyjściowego,
4. Dedykowany folder wyjściowy.

## Model iteracyjny: warstwy 0 i 1

### Warstwa 0 — Pobranie list i ekstrakcja encji
- Pobranie tabel/list z artykułów startowych.
- Konwersja wierszy do JSON records.
- Podział na kategorie (`drivers`, `constructors`, `grand_prix`, `circuits`, `seasons`).

### Warstwa 1 — Pogłębienie encji ze wskazanych punktów startowych
- Dla encji wskazanych jako wejście na dany krok pobranie stron szczegółowych.
- Parsowanie infoboxów + kluczowych sekcji.
- Standaryzacja pól (np. daty, kraje, nazwy).

### Powtarzalność (0 → 1 → 0 → 1 ...)
- Krok A: Warstwa 0 na seed listach.
- Krok B: Warstwa 1 na wynikach z Kroku A.
- Krok C: Warstwa 0 lub 1 (zgodnie z konfiguracją), ale **zawsze** na jawnie wskazanym źródle wynikowym.
- Krok D+: analogicznie, aż do osiągnięcia pożądanej głębokości.

## Struktura danych (docelowa)
- `data/raw/<category>/...` – surowe wyniki parserów.
- `data/normalized/<category>/...` – dane po normalizacji pól.
- `data/checkpoints/...` – wyniki kolejnych kroków iteracji i wskazanie źródeł kolejnego wejścia.
- `data/ml_ready/...` – materiał do modeli (kolejny etap projektu).

## Zasady jakości danych
- Idempotentne zapisy per krok (nie nadpisywać bez kontroli).
- Jawne wersjonowanie schematu rekordów.
- Raportowanie brakujących pól i konfliktów normalizacji.
- Śledzenie źródła (URL + timestamp + parser version + checkpoint input).

## Rozszerzenie o API (kolejna faza)
Po ustabilizowaniu iteracyjnego pipeline Wikipedii:
- enrichment z publicznych API (np. wyniki wyścigów, telemetria, klasyfikacje),
- deduplikacja i merge po kluczach domenowych,
- priorytety źródeł i reguły rozstrzygania konfliktów.

## Kryterium sukcesu
- Stabilny pipeline iteracyjny oparty o warstwy 0 i 1 dla kluczowych encji F1,
- Powtarzalne budowanie datasetów bez ręcznej edycji danych,
- Jasna kontrola „co jest następnym punktem startowym” na każdym kroku.
