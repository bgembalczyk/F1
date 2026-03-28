# Scrapers developer README

## New module workflow (required)

Dla **każdego nowego modułu** używaj szablonów z `scrapers/templates/`:

- `list_scraper_template.py`
- `single_scraper_template.py`

Proces: **copy + rename + fill hooks**

1. **Copy** szablon do docelowego katalogu domeny.
2. **Rename** klasy i stałe (`TODO...`) do nazewnictwa domenowego.
3. **Fill hooks/config**:
   - single scraper: `_build_infobox_payload`, `_build_tables_payload`, `_build_sections_payload`, `_assemble_record`,
   - list scraper: `SCRAPER_TEMPLATE_CONFIG`, `schema_columns`, `CONFIG`.

## Code review policy (required)

Podczas review odrzucamy PR-y, które dodają nowy scraper bez bazowania na szablonie.
Reviewer musi potwierdzić:

- użycie jednolitego kontraktu `SCRAPER_TEMPLATE_CONFIG`,
- użycie docelowych hooków bazowych (`SingleWikiArticleScraperBase` hooks dla single, `build_scraper_config` + schema DSL dla list),
- usunięcie placeholderów `TODO` przed mergem.

## Source catalog policy (required)

Nowe i istniejące scrape-ry powinny korzystać z katalogu źródeł
`scrapers/base/source_catalog.py` zamiast wpisywania URL-i ręcznie.

Zasady dodawania nowego źródła:

1. Dodaj `SourceRef` w katalogu źródeł (artykuł + opcjonalne `section_id`).
2. W `CONFIG` używaj:
   - `SOURCE.base_url` dla URL artykułu bez fragmentu,
   - `SOURCE.url()` gdy chcesz automatycznie dołączyć domyślny `section_id`,
   - `wiki_article_url(..., section_id=...)` lub `append_section_id(...)` dla niestandardowych przypadków.
3. Nie konkatenować ręcznie `\"...#section\"` w scraperach.
4. Jeśli sekcja jest dynamiczna (np. zależna od roku), trzymaj tylko artykuł w `SourceRef`,
   a `section_id` buduj w samym `CONFIG`.
