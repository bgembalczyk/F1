# Domain pipeline map

## Domain scraper spec pattern
- Każda domena listowa posiada `spec.py` z profilem `DomainScraperSpec` i funkcjami `build_*_config(...)`.
- `list_scraper.py` (lub analogiczne moduły listowe) ustawia `options_domain`, `options_profile`, `default_validator` z profilu domeny i buduje `CONFIG` przez fabrykę specyfikacji.
- Definicje kolumn powinny być wyniesione do `schemas.py` przez funkcje `build_*_schema()`, żeby ograniczyć lokalne deklaracje `schema_columns`.
