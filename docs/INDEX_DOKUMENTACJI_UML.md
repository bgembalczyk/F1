# Index - Dokumentacja UML i Analiza Struktury Projektu

## 📋 Spis Treści

### Diagramy UML (PlantUML)
1. **[uml_current_process_flow.puml](uml_current_process_flow.puml)** - Diagram przepływu procesu (obecny stan)
2. **[uml_current_class_structure.puml](uml_current_class_structure.puml)** - Struktura i hierarchia klas (obecny stan)
3. **[uml_proposed_class_structure.puml](uml_proposed_class_structure.puml)** - Proponowana uporządkowana struktura klas
4. **[uml_wiki_parser_hierarchy.puml](uml_wiki_parser_hierarchy.puml)** - Hierarchia klas WikiScrapera i WikiParserów
5. **[uml_future_dataset_pipeline.puml](uml_future_dataset_pipeline.puml)** - Docelowa wizja iteracyjnego pipeline warstw 0/1 (Wikipedia → kolejne checkpointy → ML-ready)

### Dokumentacja README
4. **[UML_DIAGRAMS_README.md](UML_DIAGRAMS_README.md)** - Kompleksowa dokumentacja w języku angielskim
5. **[UML_DIAGRAMS_README_PL.md](UML_DIAGRAMS_README_PL.md)** - Kompleksowa dokumentacja w języku polskim

### Podsumowanie
6. **[ANALIZA_STRUKTURY_PODSUMOWANIE.md](ANALIZA_STRUKTURY_PODSUMOWANIE.md)** - Podsumowanie wykonanej analizy

---

## 🎯 Szybki Start

### Jeśli chcesz zobaczyć diagramy:
👉 **Opcja 1 (najszybsza)**: Wejdź na http://www.plantuml.com/plantuml/uml/ i skopiuj zawartość pliku .puml

👉 **Opcja 2**: Zainstaluj PlantUML w VS Code i otwórz plik .puml (Alt+D aby zobaczyć)

### Jeśli chcesz zrozumieć architekturę:
👉 Zacznij od: **[UML_DIAGRAMS_README_PL.md](UML_DIAGRAMS_README_PL.md)** (polskie wyjaśnienie)

### Jeśli chcesz szybkie podsumowanie:
👉 Przeczytaj: **[ANALIZA_STRUKTURY_PODSUMOWANIE.md](ANALIZA_STRUKTURY_PODSUMOWANIE.md)**

---

## 📊 Szczegóły Diagramów

### 1. Diagram Przepływu Procesu (Current Process Flow)
**Plik**: `uml_current_process_flow.puml`
**Rozmiar**: 167 linii, 4.7KB
**Pokazuje**:
- Jak dane przepływają przez system od początku do końca
- Interakcje między komponentami
- Fazy: inicjalizacja → pobieranie → parsowanie → normalizacja → transformacja → walidacja → eksport

**Kluczowe Elementy**:
- Main.py orchestration
- HTTP fetching with caching
- Parsing strategies (table vs list)
- Validation modes (soft vs hard)
- Export to JSON/CSV

---

### 2. Struktura i Hierarchia Klas - Obecny Stan (Current Class Structure)
**Plik**: `uml_current_class_structure.puml`
**Rozmiar**: 406 linii, 11KB
**Pokazuje**:
- Hierarchię bazowych scraperów (F1Scraper → F1ListScraper/F1TableScraper/CompositeScraper)
- 30+ konkretnych implementacji scraperów
- 20+ typów kolumn dla parsowania tabel
- System infrastruktury HTTP (clients, policies, cache)
- Modele danych i fabryki rekordów
- System walidacji

**Główne Pakiety**:
- Base Scrapers
- Specialized Base Classes
- Concrete Scrapers (Circuits, Drivers, Constructors, Engines, etc.)
- Column Types
- Infrastructure (HTTP, Caching, Policies)
- Models & Data
- Validation

---

### 4. Hierarchia WikiScraper i WikiParserów
**Plik**: `uml_wiki_parser_hierarchy.puml`

**Pokazuje**:
- Klasę `WikiScraper` (pobiera HTML – jest scraperem; używa http_client z opcjonalnym cache)
- Abstrakcyjną klasę bazową `WikiParser`
- Parsery poziomu strony: `HeaderParser`, `BodyContentParser`, `CategoryLinksParser`, `ContentTextParser`
- Parsery sekcji: `SectionParser` → `SubSectionParser` → `SubSubSectionParser` → `SubSubSubSectionParser`
- Parsery elementów HTML: `InfoboxParser`, `ParagraphParser`, `FigureParser`, `ListParser`, `TableParser`, `NavBoxParser`, `ReferencesWrapParser`
- Mixin `WikiElementParserMixin` dostarczający narzędzia elementarne do parserów sekcji

**Zasady architektury** widoczne w diagramie:
- Klasa pobierająca HTML = **Scraper** (http_client obsługuje cache)
- Klasa obsługująca wiele scraperów = **DataExtractor**
- Sekcje zaczynające się bez nagłówka noszą nazwę `(Top)`
- Każdy poziom sekcji deleguje parsowanie do niższego poziomu

---

### 3. Proponowana Struktura - Ulepszona (Proposed Class Structure)
**Plik**: `uml_proposed_class_structure.puml`
**Rozmiar**: 629 linii, 16KB
**Pokazuje**:
- Architekturę zgodną z zasadami SOLID
- Interfejsy dla wszystkich głównych komponentów
- Wzorce projektowe: Strategy, Pipeline, Factory, Decorator
- Separację odpowiedzialności
- Elastyczną kompozycję

**Kluczowe Ulepszenia**:
- ✅ Single Responsibility - każda klasa ma jedną odpowiedzialność
- ✅ Interface-based design - zależności od abstrakcji
- ✅ Strategy Pattern - zamienne implementacje
- ✅ Pipeline Pattern - elastyczne etapy przetwarzania
- ✅ Factory Pattern - centralne tworzenie rekordów
- ✅ Testability - łatwe testowanie w izolacji

---

## 📚 Dokumentacja

### README po Angielsku
**Plik**: `UML_DIAGRAMS_README.md`
**Rozmiar**: 282 linie, 9.8KB

**Zawiera**:
- Szczegółowy opis każdego diagramu
- Wyjaśnienie kluczowych komponentów
- Analiza problemów w obecnej architekturze
- 6-fazowy plan migracji do nowej architektury
- Instrukcje przeglądania diagramów
- Odniesienia do powiązanej dokumentacji

---

### README po Polsku
**Plik**: `UML_DIAGRAMS_README_PL.md`
**Rozmiar**: 227 linii, 7.9KB

**Zawiera**:
- Przegląd wszystkich diagramów
- Opis obecnych problemów
- Plan migracji
- Instrukcje przeglądania

---

### Podsumowanie Analizy
**Plik**: `ANALIZA_STRUKTURY_PODSUMOWANIE.md`
**Rozmiar**: 275 linii, 8.0KB

**Zawiera**:
- Streszczenie wykonanej analizy
- Statystyki utworzonych plików
- Identyfikacja problemów architektonicznych
- Proponowane rozwiązania
- Ścieżka migracji (6 faz, 10-15 tygodni)
- Instrukcje korzystania z diagramów

---

## 🔍 Zidentyfikowane Problemy

### 1. God Object Anti-pattern
`F1Scraper` ma zbyt wiele odpowiedzialności - obsługuje wszystko od pobierania do eksportu.

### 2. Tight Coupling
Scrapery silnie powiązane z konkretnymi implementacjami parserów i validatorów.

### 3. Brak Abstrakcji
Ograniczone użycie interfejsów, trudno zamienić implementacje.

### 4. Duplikacja Kodu
Podobna logika powtarza się w różnych scraperach.

### 5. Złożoność Konfiguracji
Konfiguracja rozproszona w wielu miejscach.

---

## 💡 Proponowane Rozwiązania

### SOLID Principles
- ✅ **Single Responsibility**: Każda klasa ma jedną odpowiedzialność
- ✅ **Open/Closed**: Łatwe rozszerzanie bez modyfikacji
- ✅ **Liskov Substitution**: Interfejsy umożliwiają zamienność
- ✅ **Interface Segregation**: Małe, skoncentrowane interfejsy
- ✅ **Dependency Inversion**: Zależność od abstrakcji

### Design Patterns
- 🎯 **Strategy Pattern**: Zamienne strategie parsowania/walidacji/normalizacji
- 🎯 **Pipeline Pattern**: Elastyczna kompozycja etapów przetwarzania
- 🎯 **Factory Pattern**: Centralne tworzenie rekordów
- 🎯 **Decorator Pattern**: Funkcjonalność cache jako dekorator

---

## 🛠️ Narzędzia do Przeglądania

### PlantUML Online (najłatwiejsze)
```
1. Wejdź na: http://www.plantuml.com/plantuml/uml/
2. Skopiuj zawartość pliku .puml
3. Wklej i zobacz diagram
```

### VS Code (zalecane dla developerów)
```
1. Zainstaluj rozszerzenie "PlantUML"
2. Otwórz plik .puml
3. Naciśnij Alt+D
```

### Command Line
```bash
# Instalacja
sudo apt-get install plantuml

# Generowanie PNG
plantuml docs/uml_current_process_flow.puml

# Generowanie SVG (lepsza jakość)
plantuml -tsvg docs/*.puml
```

### Docker
```bash
docker run -v $(pwd)/docs:/data plantuml/plantuml:latest -tpng /data/*.puml
```

---

## 📈 Statystyki

### Utworzone Pliki
- **6 nowych plików** w folderze `docs/`
- **1,986 linii** kodu/dokumentacji
- **~46KB** całkowitej zawartości

### Podział
- **3 diagramy UML**: 1,202 linie PlantUML (~32KB)
- **2 README**: 509 linii dokumentacji (~18KB)
- **1 podsumowanie**: 275 linii (~8KB)

---

## 🗺️ Ścieżka Migracji

### Faza 1: Interfejsy (1-2 tygodnie)
Wprowadzenie IDataSource, IParser, IValidator, ITransformer, IExporter, IRecordFactory

### Faza 2: Strategie (2-3 tygodnie)
Ekstrakcja logiki parsowania, walidacji i normalizacji do osobnych klas

### Faza 3: Pipeline (1-2 tygodnie)
Implementacja ProcessingPipeline z wymiennymi etapami

### Faza 4: Fabryki (1-2 tygodnie)
BaseRecordFactory, wyspecjalizowane fabryki, RecordFactoryRegistry

### Faza 5: Konfiguracja (1 tydzień)
ScraperConfiguration, migracja istniejącej konfiguracji

### Faza 6: Refaktoryzacja (3-4 tygodnie)
Nowe klasy bazowe, migracja scraperów, usunięcie starych klas

**Łączny czas**: 10-15 tygodni

---

## 📎 Powiązana Dokumentacja

- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Historia poprzednich refaktoryzacji
- [RAPORT_REFAKTORYZACJI_2026.md](RAPORT_REFAKTORYZACJI_2026.md) - Szczegółowy raport refaktoryzacji
- [PODSUMOWANIE_REFAKTORYZACJI.md](PODSUMOWANIE_REFAKTORYZACJI.md) - Podsumowanie refaktoryzacji
- [normalization.md](normalization.md) - Dokumentacja normalizacji danych

---

## 👤 Informacje

**Analiza wykonana**: 2026-01-08
**Narzędzie**: GitHub Copilot
**Format diagramów**: PlantUML
**Języki dokumentacji**: English, Polski

---

## ❓ Pytania?

Jeśli masz pytania dotyczące architektury lub diagramów:
1. Przejrzyj powiązaną dokumentację
2. Sprawdź komentarze w bazowych klasach
3. Otwórz issue z konkretnymi pytaniami

---

**Sukces!** 🎉 Wszystkie diagramy UML i dokumentacja zostały pomyślnie utworzone!
