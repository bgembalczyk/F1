# Diagramy UML - Projekt F1 Wikipedia Scraper

## Przegląd

Niniejszy katalog zawiera diagramy UML dokumentujące architekturę projektu F1 Wikipedia Scraper. Diagramy ilustrują zarówno aktualny stan systemu, jak i proponowane ulepszenia.

## Diagramy

### 1. Aktualny Przepływ Procesu (`uml_current_process_flow.puml`)

**Cel**: Pokazuje jak dane przepływają przez system od początku do końca.

**Kluczowe Procesy**:
- **Inicjalizacja**: Jak main.py orkiestruje różne scrapery
- **Faza Pobierania**: Pobieranie HTTP z mechanizmem cache'owania
- **Faza Parsowania**: Konwersja HTML do strukturyzowanych danych
- **Faza Normalizacji**: Czyszczenie i standaryzacja danych
- **Faza Transformacji**: Stosowanie przekształceń danych
- **Faza Walidacji**: Walidacja rekordów (tryb twardy vs miękki)
- **Faza Post-Processingu**: Finalne przetwarzanie rekordów
- **Faza Eksportu**: Zapis do plików JSON/CSV

**Główne Komponenty**:
- `main.py` - Punkt wejścia uruchamiający scrapery
- `F1Scraper` - Bazowy scraper orkiestrujący pipeline
- `HttpClient` & `CacheAdapter` - Pobieranie HTTP z cache'owaniem plikowym
- `Parser` - Konwertuje HTML na rekordy (tabele lub listy)
- `Normalizer` - Standaryzuje wartości pól
- `Transformer` - Stosuje transformacje danych
- `Validator` - Waliduje rekordy z konfigurowalnymi trybami
- `Exporter` - Eksportuje do JSON/CSV

**Typy Przepływów**:
1. **List Scrapers**: Prosta ekstrakcja tabel/list ze stron Wikipedia
2. **Complete Scrapers**: Wzorzec kompozytu - pobiera listę, potem szczegóły dla każdego elementu

### 2. Obecna Struktura i Hierarchia Klas (`uml_current_class_structure.puml`)

**Cel**: Dokumentuje obecny projekt obiektowy i relacje dziedziczenia.

**Kluczowe Hierarchie Klas**:

#### Bazowe Scrapery
- `F1Scraper` - Abstrakcyjna baza z pipeline fetch/parse/validate/export
- `F1ListScraper` - Do parsowania list HTML (elementy ul/ol)
- `F1TableScraper` - Do parsowania tabel Wikipedia z konfigurowalnymi schematami
- `CompositeScraper` - Łączy scrapery list + szczegółów

#### Wyspecjalizowane Klasy Bazowe
- `IndianapolisOnlyListScraper` - Dla list specyficznych dla Indianapolis 500
- `BaseEngineTableScraper` - Baza dla tabel związanych z silnikami
- `BasePointsScraper` - Baza dla tabel systemów punktowych

#### Konkretne Implementacje
- **Circuits**: `CircuitsListScraper`, `F1SingleCircuitScraper`, `F1CompleteCircuitScraper`
- **Drivers**: `F1DriversListScraper`, `FemaleDriversListScraper`, `F1FatalitiesListScraper`
- **Constructors**: `CurrentConstructorsListScraper`, `FormerConstructorsListScraper`, etc.
- **Engines**: `EngineManufacturersListScraper`, `EngineRegulationScraper`, etc.
- **Grands Prix**: `F1CompleteGrandPrixScraper`, `RedFlaggedRacesScraper`, etc.

#### System Typów Kolumn
- `BaseColumn` - Abstrakcyjna baza dla parsowania kolumn
- 20+ wyspecjalizowanych typów kolumn

#### Modele Danych
- Klasy rekordów: `Circuit`, `Driver`, `Constructor`, `Season`
- `RecordFactory` - Metody fabrykujące dla tworzenia typowanych rekordów
- `FieldNormalizer` - Statyczne metody normalizacji pól

### 3. Proponowana Ulepszona Struktura Klas (`uml_proposed_class_structure.puml`)

**Cel**: Proponuje ulepszoną architekturę zgodną z zasadami SOLID i wzorcami projektowymi.

**Kluczowe Ulepszenia**:

#### 1. Separacja Odpowiedzialności
- **Obecne**: Scrapery obsługują pobieranie, parsowanie, walidację i eksport
- **Proponowane**: Każda odpowiedzialność to osobny komponent z jasnymi interfejsami

#### 2. Projekt Oparty na Interfejsach
- `IDataSource` - Abstrakcyjne pobieranie danych
- `IParser` - Abstrakcyjna logika parsowania
- `IValidator` - Abstrakcyjna walidacja
- `ITransformer` - Abstrakcyjne transformacje
- `IExporter` - Abstrakcyjna logika eksportu
- `IRecordFactory` - Abstrakcyjne tworzenie rekordów

#### 3. Implementacja Wzorca Strategii

**Strategie Parsowania**:
- `ListParser` - Dla treści opartych na listach
- `TableParser` - Dla treści opartych na tabelach
- `InfoboxParser` - Dla infoboxów Wikipedia

**Strategie Normalizacji**:
- `IntNormalizationStrategy`
- `FloatNormalizationStrategy`
- `LinkNormalizationStrategy`
- `SeasonListNormalizationStrategy`
- `DateNormalizationStrategy`

**Strategie Walidacji**:
- `RequiredFieldRule`
- `TypeCheckRule`
- `RangeValidationRule`
- `CustomValidationRule`

#### 4. Wzorzec Pipeline
- `ProcessingPipeline` - Komponuje etapy przetwarzania
- `IPipelineStage` - Interfejs dla etapów pipeline
- Etapy: `NormalizationStage`, `TransformationStage`, `ValidationStage`

**Korzyści**:
- Łatwe dodawanie/usuwanie etapów
- Przejrzysty przepływ danych
- Testowalne w izolacji

#### 5. Wzorzec Fabryki
- `BaseRecordFactory` - Wspólna logika tworzenia rekordów
- `RecordFactoryRegistry` - Centralny rejestr fabryk
- Wyspecjalizowane fabryki: `CircuitRecordFactory`, `DriverRecordFactory`, etc.

## Obecne Problemy w Architekturze

### 1. Antywzorzec God Object
- `F1Scraper` ma zbyt wiele odpowiedzialności
- Obsługuje pobieranie, parsowanie, normalizację, walidację, transformację i eksport

### 2. Silne Powiązania
- Scrapery silnie powiązane z konkretnymi parserami
- Trudno zamienić strategie parsowania
- Trudne testowanie komponentów w izolacji

### 3. Brak Abstrakcji
- Wiele implementacji zależy od konkretnych klas
- Ograniczone użycie interfejsów
- Trudno zapewnić alternatywne implementacje

### 4. Duplikacja
- Podobna logika parsowania w różnych scraperach
- Powtarzające się wzorce walidacji
- Copy-paste w konkretnych scraperach

### 5. Złożoność Konfiguracji
- Konfiguracja rozproszona w wielu miejscach
- Trudno zrozumieć jakie opcje są dostępne

## Ścieżka Migracji

Aby przejść z obecnej do proponowanej architektury:

### Faza 1: Wprowadzenie Interfejsów
1. Zdefiniowanie podstawowych interfejsów
2. Utworzenie klas adapterowych
3. Aktualizacja testów

### Faza 2: Ekstrakcja Strategii
1. Ekstrakcja logiki parsowania do klas strategii
2. Ekstrakcja logiki walidacji do systemu reguł
3. Ekstrakcja normalizacji do klas strategii

### Faza 3: Implementacja Pipeline
1. Utworzenie klasy `ProcessingPipeline`
2. Migracja normalizacji/transformacji/walidacji do etapów
3. Aktualizacja scraperów do użycia pipeline

### Faza 4: Refaktoryzacja Fabryk
1. Implementacja `BaseRecordFactory`
2. Utworzenie wyspecjalizowanych fabryk
3. Wprowadzenie `RecordFactoryRegistry`

### Faza 5: Wprowadzenie Konfiguracji
1. Utworzenie klas `ScraperConfiguration`
2. Migracja istniejących konfiguracji
3. Usunięcie zakodowanej konfiguracji

### Faza 6: Refaktoryzacja Scraperów
1. Utworzenie nowych bazowych klas scraperów
2. Migracja konkretnych scraperów jeden po drugim
3. Usunięcie starych klas bazowych po migracji wszystkich

## Jak Przeglądać Diagramy

### Użycie PlantUML Online
1. Wejdź na http://www.plantuml.com/plantuml/uml/
2. Skopiuj zawartość dowolnego pliku `.puml`
3. Wklej i zobacz renderowany diagram

### Użycie VS Code
1. Zainstaluj rozszerzenie "PlantUML"
2. Otwórz dowolny plik `.puml`
3. Naciśnij `Alt+D` aby zobaczyć podgląd

### Użycie Linii Poleceń
```bash
# Instalacja PlantUML
sudo apt-get install plantuml

# Generowanie PNG
plantuml uml_current_process_flow.puml
plantuml uml_current_class_structure.puml
plantuml uml_proposed_class_structure.puml

# Generowanie SVG (skalowalne)
plantuml -tsvg *.puml
```

### Użycie Dockera
```bash
docker run -v $(pwd):/data plantuml/plantuml:latest -tpng /data/*.puml
```

## Powiązana Dokumentacja

- `REFACTORING_SUMMARY.md` - Podsumowanie poprzednich prac refaktoryzacyjnych
- `RAPORT_REFAKTORYZACJI_2026.md` - Szczegółowy raport refaktoryzacji
- `PODSUMOWANIE_REFAKTORYZACJI.md` - Podsumowanie refaktoryzacji
- `normalization.md` - Dokumentacja normalizacji danych

## Wkład do Projektu

Przy dokonywaniu zmian architektonicznych:

1. Zaktualizuj odpowiednie diagramy UML
2. Udokumentuj uzasadnienie w komentarzach commit
3. Zaktualizuj ten README jeśli wprowadzane są nowe wzorce
4. Rozważ ścieżkę migracji z obecnej do proponowanej architektury
