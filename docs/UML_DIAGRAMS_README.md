# UML Diagrams - F1 Wikipedia Scraper Project

## Overview

This directory contains UML diagrams documenting the architecture of the F1 Wikipedia Scraper project. The diagrams illustrate both the current state of the system and proposed improvements.

## Diagrams

### 1. Current Process Flow (`uml_current_process_flow.puml`)

**Purpose**: Shows how data flows through the system from start to finish.

**Key Processes Illustrated**:
- **Initialization**: How the main.py orchestrates different scrapers
- **Download Phase**: HTTP fetching with caching mechanism
- **Parse Phase**: Converting HTML to structured data (table vs list parsing)
- **Normalize Phase**: Cleaning and standardizing data
- **Transform Phase**: Applying data transformations
- **Validation Phase**: Validating records (hard mode vs soft mode)
- **Post-Process Phase**: Final record processing
- **Export Phase**: Writing to JSON/CSV files

**Main Components**:
- `main.py` - Entry point that runs list and complete scrapers
- `F1Scraper` - Base scraper orchestrating the pipeline
- `HttpClient` & `CacheAdapter` - HTTP fetching with file-based caching
- `Parser` - Converts HTML to records (table or list based)
- `Normalizer` - Standardizes field values
- `Transformer` - Applies transformations (e.g., championships parsing)
- `Validator` - Validates records with configurable modes
- `Exporter` - Exports to JSON/CSV

**Flow Types**:
1. **List Scrapers**: Simple table/list extraction from Wikipedia pages
2. **Complete Scrapers**: Composite pattern - fetch list, then details for each item

### 2. Current Class Structure and Hierarchy (`uml_current_class_structure.puml`)

**Purpose**: Documents the current object-oriented design and inheritance relationships.

**Key Class Hierarchies**:

#### Base Scrapers
- `F1Scraper` - Abstract base with fetch/parse/validate/export pipeline
- `F1ListScraper` - For parsing HTML lists (ul/ol elements)
- `F1TableScraper` - For parsing Wikipedia tables with configurable schemas
- `CompositeScraper` - Combines list + detail scrapers

#### Specialized Base Classes
- `IndianapolisOnlyListScraper` - For Indianapolis 500 specific lists
- `BaseEngineTableScraper` - Base for engine-related tables
- `BasePointsScraper` - Base for points system tables

#### Concrete Implementations
- **Circuits**: `CircuitsListScraper`, `F1SingleCircuitScraper`, `F1CompleteCircuitScraper`
- **Drivers**: `F1DriversListScraper`, `FemaleDriversListScraper`, `F1FatalitiesListScraper`
- **Constructors**: `CurrentConstructorsListScraper`, `FormerConstructorsListScraper`, etc.
- **Engines**: `EngineManufacturersListScraper`, `EngineRegulationScraper`, etc.
- **Grands Prix**: `F1CompleteGrandPrixScraper`, `RedFlaggedRacesScraper`, etc.
- **Other**: `SeasonsListScraper`, `PointsScoringSystemsHistoryScraper`, etc.

#### Column Types System
- `BaseColumn` - Abstract base for column parsing
- 20+ specialized column types: `TextColumn`, `IntColumn`, `DriverListColumn`, `SeasonsColumn`, etc.

#### Infrastructure
- HTTP clients with policy pattern (retry, rate limiting, caching)
- Cache adapters for file-based caching

#### Data Models
- Record classes: `Circuit`, `Driver`, `Constructor`, `Season`
- `RecordFactory` - Factory methods for creating typed records
- `FieldNormalizer` - Static methods for field normalization

#### Validation
- `RecordValidator` - Base validator with stats collection
- Specialized validators: `CircuitsRecordValidator`, `DriversRecordValidator`, etc.

### 3. Proposed Improved Class Structure (`uml_proposed_class_structure.puml`)

**Purpose**: Proposes an improved architecture following SOLID principles and design patterns.

**Key Improvements**:

#### 1. Separation of Concerns
- **Current**: Scrapers handle fetching, parsing, validation, and export
- **Proposed**: Each concern is a separate component with clear interfaces

#### 2. Interface-Based Design
- `IDataSource` - Abstract data fetching
- `IParser` - Abstract parsing logic
- `IValidator` - Abstract validation
- `ITransformer` - Abstract transformations
- `IExporter` - Abstract export logic
- `IRecordFactory` - Abstract record creation

#### 3. Strategy Pattern Implementation

**Parsing Strategies**:
- `ListParser` - For list-based content
- `TableParser` - For table-based content
- `InfoboxParser` - For Wikipedia infoboxes
- All implement `IParser` interface

**Normalization Strategies**:
- `IntNormalizationStrategy`
- `FloatNormalizationStrategy`
- `LinkNormalizationStrategy`
- `SeasonListNormalizationStrategy`
- `DateNormalizationStrategy`

**Validation Strategies**:
- `RequiredFieldRule`
- `TypeCheckRule`
- `RangeValidationRule`
- `CustomValidationRule`

#### 4. Pipeline Pattern
- `ProcessingPipeline` - Composes processing stages
- `IPipelineStage` - Interface for pipeline stages
- Stages: `NormalizationStage`, `TransformationStage`, `ValidationStage`

**Benefits**:
- Easy to add/remove stages
- Clear data flow
- Testable in isolation

#### 5. Factory Pattern
- `BaseRecordFactory` - Common record creation logic
- `RecordFactoryRegistry` - Central registry for factories
- Specialized factories: `CircuitRecordFactory`, `DriverRecordFactory`, etc.

#### 6. Improved Column Parsing
- `BaseColumnParser` - Abstract column parser
- `ColumnParserFactory` - Creates parsers based on type
- Specialized parsers: `TextColumnParser`, `NumericColumnParser`, `LinkColumnParser`, etc.

#### 7. Enhanced Data Access Layer
- `HttpDataSource` - HTTP fetching
- `CachedDataSource` - Decorator for caching
- `PolicyBasedHttpClient` - Policy pattern for HTTP concerns
- Clean separation of concerns

#### 8. Configuration Management
- `ScraperConfiguration` - Central configuration
- `ParserConfig` - Parser-specific settings
- `ValidationConfig` - Validation settings
- `ExportConfig` - Export settings

**Benefits of Proposed Architecture**:

1. **Single Responsibility**: Each class has one clear purpose
2. **Open/Closed**: Easy to extend without modifying existing code
3. **Liskov Substitution**: Interfaces enable substitutability
4. **Interface Segregation**: Small, focused interfaces
5. **Dependency Inversion**: Depend on abstractions, not implementations
6. **Better Testability**: Each component can be tested in isolation
7. **Flexibility**: Easy to swap implementations
8. **Maintainability**: Clear structure and dependencies
9. **Reusability**: Components can be reused across scrapers
10. **Extensibility**: Easy to add new scrapers, parsers, validators

## Current Issues in the Architecture

### 1. God Object Anti-pattern
- `F1Scraper` has too many responsibilities
- Handles fetching, parsing, normalization, validation, transformation, and export

### 2. Tight Coupling
- Scrapers tightly coupled to specific parsers
- Hard to swap parsing strategies
- Difficult to test components in isolation

### 3. Lack of Abstraction
- Many implementations depend on concrete classes
- Limited use of interfaces
- Hard to provide alternative implementations

### 4. Duplication
- Similar parsing logic across different scrapers
- Repeated validation patterns
- Copy-paste in concrete scrapers

### 5. Configuration Complexity
- Configuration spread across multiple places
- `ScraperConfig`, inline configs, class attributes
- Hard to understand what options are available

### 6. Limited Extensibility
- Adding new scraper types requires inheritance
- Can't easily compose scrapers from existing components
- Rigid structure

## Migration Path

To transition from current to proposed architecture:

### Phase 1: Introduce Interfaces
1. Define core interfaces (`IDataSource`, `IParser`, `IValidator`, etc.)
2. Create adapter classes that wrap existing implementations
3. Update tests to use interfaces

### Phase 2: Extract Strategies
1. Extract parsing logic into strategy classes
2. Extract validation logic into rule-based system
3. Extract normalization into strategy classes

### Phase 3: Implement Pipeline
1. Create `ProcessingPipeline` class
2. Migrate normalization/transformation/validation to stages
3. Update scrapers to use pipeline

### Phase 4: Refactor Factories
1. Implement `BaseRecordFactory`
2. Create specialized factories
3. Introduce `RecordFactoryRegistry`

### Phase 5: Introduce Configuration
1. Create `ScraperConfiguration` classes
2. Migrate existing configs
3. Remove hard-coded configuration

### Phase 6: Refactor Scrapers
1. Create new scraper base classes
2. Migrate concrete scrapers one by one
3. Remove old base classes when all migrated

## How to View the Diagrams

### Using PlantUML Online
1. Go to http://www.plantuml.com/plantuml/uml/
2. Copy the content of any `.puml` file
3. Paste and view the rendered diagram

### Using VS Code
1. Install the "PlantUML" extension
2. Open any `.puml` file
3. Press `Alt+D` to preview

### Using Command Line
```bash
# Install PlantUML
sudo apt-get install plantuml

# Generate PNG
plantuml uml_current_process_flow.puml
plantuml uml_current_class_structure.puml
plantuml uml_proposed_class_structure.puml

# Generate SVG (scalable)
plantuml -tsvg uml_current_process_flow.puml
plantuml -tsvg uml_current_class_structure.puml
plantuml -tsvg uml_proposed_class_structure.puml
```

### Using Docker
```bash
docker run -v $(pwd):/data plantuml/plantuml:latest -tpng /data/*.puml
```

## Related Documentation

- `REFACTORING_SUMMARY.md` - Summary of previous refactoring efforts
- `RAPORT_REFAKTORYZACJI_2026.md` - Detailed refactoring report
- `PODSUMOWANIE_REFAKTORYZACJI.md` - Refactoring summary in Polish
- `normalization.md` - Documentation on data normalization

## Contributing

When making architectural changes:

1. Update the relevant UML diagrams
2. Document the rationale in commit messages
3. Update this README if new patterns are introduced
4. Consider the migration path from current to proposed architecture

## Questions?

If you have questions about the architecture or diagrams, please:
1. Review the related documentation files
2. Check the code comments in base classes
3. Open an issue with specific questions
