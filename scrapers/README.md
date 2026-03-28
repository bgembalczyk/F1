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


## Extension guide

Szczegółowy przewodnik rozszerzania (hooki obowiązkowe, punkty rozszerzeń, antywzorce, minimalne przykłady):

- `docs/architecture/scraper-extension-guide.md`
## Helper modules (capability-first)
- Unikaj jednego worka `helpers` z funkcjami o mieszanej odpowiedzialności.
- Grupuj helpery wg capability (np. `text`, `links`, `tables`, `sections`).
- Funkcje współdzielone między domenami dodawaj **najpierw** do `scrapers/base/helpers/`.
- Dopiero gdy logika jest domenowa i nie ma sensu jej uogólniać, trzymaj ją lokalnie w domenie.
- Dla funkcji przenoszonych między modułami utrzymuj jedno źródło prawdy (bez duplikatów).
