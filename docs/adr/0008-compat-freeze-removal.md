# ADR-0008: Compat freeze removal i rollout finalizacji API

- **Status:** Accepted
- **Data:** 2026-04-11
- **Autor:** zespół F1 platform
- **Decydenci:** maintainers warstw `scrapers/*`, `models/*`, `layers/*`
- **Dotyczy:** usunięcie aktywnego wsparcia przejściowego (`compat`, `protocol2`, aliasy `RecordFactory`)

## Kontekst

Po domknięciu migracji nazewnictwa i kontraktów utrzymywanie aktywnych ścieżek przejściowych zwiększa koszt review i utrudnia egzekwowanie granic architektonicznych. Potrzebujemy jednej daty odcięcia i jednego miejsca z checklistą rolloutową.

## Decyzja

1. **Data „compat freeze removal”: 2026-05-15 (UTC).**
2. Od tej daty:
   - nie dodajemy nowych importów do modułów `compat`/`protocol2`/`*_deprecated*`,
   - nie dodajemy nowych aliasów typu `RecordFactory = ...`,
   - dokumentacja i testy referują wyłącznie kontrakty kanoniczne.
3. Centralnym mechanizmem egzekwowania jest architektoniczny **compat debt gate**:
   - `tests/architecture/test_compat_debt_gate.py`.

## Przegląd testów z frazami `legacy` / `deprecated` / `compatibility`

### A. Testy do usunięcia (dotyczą tylko legacy API)

- `tests/test_cli_legacy_profiles.py`
- `tests/test_cli_deprecation_runtime.py`
- `tests/test_deprecated_elements_report_ci.py`
- `tests/contract/test_result_export_compatibility.py`
- `tests/test_seed_registry_import_compat.py`

Kryterium: test sprawdza wyłącznie zachowanie aliasu/wrappera/deprecation-warning i nie wnosi pokrycia dla kontraktu kanonicznego.

### B. Testy do przepięcia na kontrakt kanoniczny

- `tests/test_seed_registry_generation.py`
- `tests/test_wiki_seed_registry.py`
- `tests/test_sources_registry_extra.py`
- `tests/test_record_factories_snapshot_compat.py`
- `tests/test_record_factories.py` (sekcje kompatybilnościowe)
- `tests/test_section_parser_regressions.py` (przypadki „legacy fallback”)
- `tests/test_points_scraper_composition.py` (ścieżki „legacy fallback”)

Kierunek przepięcia: ten sam scenariusz biznesowy, ale asercje na zachowanie kanoniczne (bez aliasów i bez ostrzeżeń deprecacyjnych jako celu testu).

## Checklista rolloutu

### Kod
- [ ] Usunąć moduły aliasowe `compat`/`protocol2`/`*_deprecated*` lub ograniczyć je do minimum technicznego wymaganego przez freeze.
- [ ] Zastąpić importy aliasowe importami kanonicznymi.
- [ ] Usunąć aliasy `RecordFactory = ...` poza miejscami jawnie dopuszczonymi do czasu terminu.
- [ ] Utrzymać zielony wynik `tests/architecture/test_compat_debt_gate.py`.

### Testy
- [ ] Usunąć testy z grupy A.
- [ ] Przepiąć testy z grupy B na kontrakty kanoniczne.
- [ ] Dodać regresję dla każdej usuniętej ścieżki kompatybilności (regresja ma potwierdzać brak użycia legacy, nie jego działanie).

### Dokumentacja
- [ ] Usunąć z dokumentacji sformułowania o aktywnym wsparciu przejściowym.
- [ ] Utrzymywać mapy migracji jako mapy historyczne + status „migration closed”.
- [ ] Linkować ten ADR z kolejnych zmian czyszczących legacy.

## Konsekwencje

- Plusy:
  - wyraźna data odcięcia i jeden punkt kontroli długu kompatybilności.
  - mniejsze ryzyko „cichego” odtwarzania aliasów podczas refaktoryzacji.
- Minusy / trade-offy:
  - konieczność przepięcia części testów i krótkoterminowy koszt porządkowy.
