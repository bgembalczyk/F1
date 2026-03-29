# Plan dojścia do docelowej architektury (taski)

> Ten plik jest źródłem prawdy przy zadaniach typu „zaplanuj kolejne taski”.
> Status aktualizujemy checkboxami: `[ ]` / `[x]`.

## Etap 1 — Fundament seed scraperów (Warstwa 0)
- [x] Zdefiniować listę stron startowych (kierowcy, konstruktorzy, GP, tory, sezony).
  - Potwierdzenie: istnieją dedykowane list scrape'ry dla kluczowych seedów (`drivers`, `constructors`, `grands_prix`, `circuits`, `seasons`).
  - Moduły referencyjne: `scrapers/drivers/list_scraper.py`, `scrapers/constructors/*_list*.py`, `scrapers/grands_prix/list_scraper.py`, `scrapers/circuits/list_scraper.py`, `scrapers/seasons/list_scraper.py`.
- [x] Dodać konfigurację mapującą: `seed_name -> wikipedia_url -> output_category`.
  - Status migracji: centralny moduł ścieżek (`DataPaths`) oraz rejestr seedów/list jobów został rozszerzony o ścieżki docelowe (`data/raw/...`) i legacy (`data/wiki/...`) do bezpiecznej migracji.
- [ ] Ustalić minimalny wspólny schemat rekordu seed (`name`, `link`, `source_url`, `scraped_at`).
- [x] Wdrożyć eksport JSON dla każdej kategorii do `data/raw/<category>/`.
  - Status migracji: writer seed L0 wspiera bezpośredni zapis przez `DataPaths` do `data/raw/<category>/...`.
- [ ] Dodać logowanie jakości: liczba rekordów, puste pola, duplikaty.

## Etap 2 — Parsery encji szczegółowych (Warstwa 1)
- [ ] Dodać parser infoboxów dla stron encji (driver/constructor/circuit/grand_prix/season).
  - Status: częściowo zrobione dla `driver`/`constructor`/`circuit`; brak spójnego domknięcia dla całego kompletu encji 1:1 z roadmapą.
- [ ] Znormalizować kluczowe pola (daty, kraj, aliasy nazw).
- [ ] Dodać mapowanie i wersjonowanie schematów rekordów.
- [ ] Zapisywać wynik w `data/normalized/<category>/`.

## Etap 3 — Iteracyjny orchestrator 0/1 (na sztywno)
- [ ] Zaimplementować orchestrator kroków z ręcznie określonym zakresem przejść 0/1.
- [ ] Dla każdego kroku jawnie wskazać źródło kolejnych punktów startowych (`checkpoint_input`).
- [ ] Dodać rejestr kroków: `krok -> skąd wejście -> jaki parser -> gdzie wyjście`.
- [ ] Zapewnić, że nie scrapujemy ponownie danych już przetworzonych bez potrzeby.

## Etap 4 — Stabilność i obserwowalność pipeline
- [ ] Dodać metryki pipeline (czas, liczba rekordów, błędy parserów).
- [ ] Dodać raporty jakości po każdym kroku iteracji.
- [ ] Dodać testy parserów na snapshotach HTML.
- [x] Dodać retry/backoff dla fetchowania stron.
  - Potwierdzenie: opcje `http_retries` i `http_backoff_seconds` są częścią konfiguracji scrapera i HTTP klienta.
  - Moduły referencyjne: `scrapers/base/options.py`, `scrapers/base/run_config.py`, `infrastructure/http_client/config.py`.

## Etap 5 — Przygotowanie pod ML (później)
- [ ] Zdefiniować cechy i słowniki tokenizacji.
- [ ] Dodać etap kodowania cech do `data/ml_ready/`.
- [ ] Zbudować wersjonowane zestawy treningowe.

## Nowe zadania wynikające z aktualnych luk
- [x] Adapter sekcji: wprowadzić warstwę `SectionSourceAdapter` dla pobierania „kolejnych punktów startowych” bezpośrednio z `data/checkpoints/*.json` (z fallbackiem do `data/raw/*`).
  - Status migracji: dodany fallback kompatybilności do legacy ścieżek `data/wiki/<domain>/*.json`.
- [ ] Orchestrator 0/1: dodać jawny `StepOrchestrator` (hardcoded flow) wykonujący kroki `L0 -> L1 -> L0/L1` z deklaratywnym `checkpoint_input` i rejestrem kroków.
- [x] Migracja output layout: przejść z obecnego `data/wiki/...` na layout docelowy (`data/raw`, `data/normalized`, `data/checkpoints`) z mapą kompatybilności ścieżek i etapem migracyjnym.
  - Status migracji: dodano skrypt `scripts/migrate_data_layout.py` mapujący stare pliki do nowego layoutu oraz raportujący brakujące pliki/kolizje.

## Reguły wersjonowania i layout plików danych
- Struktura katalogów jest wersjonowana semantycznie przez layout (`v1`):
  - `data/raw/<domain>/list/*.json` — wyniki list/seed scraperów (warstwa surowa),
  - `data/normalized/<domain>/*.json` — rekordy po normalizacji,
  - `data/checkpoints/step_<id>_<layer>_<domain>.json` — checkpointy pipeline.
- Każda zmiana łamiąca kompatybilność nazewnictwa plików powinna:
  1. utrzymać fallback odczytu legacy co najmniej przez jeden cykl migracyjny,
  2. dodać mapowanie w skrypcie migracyjnym,
  3. zostać odnotowana w tej roadmapie jako status migracji.

## Następne 3 konkretne taski (short-term)
- [ ] Task A: Utworzyć konfigurację seed URL-i i kategorii wyjściowych.
  - Skąd bierzemy kolejne punkty startowe: wejście inicjalne z `data/wiki/drivers/f1_drivers.json` oraz `data/wiki/constructors/f1_former_constructors.json` jako bootstrap do pierwszego checkpointu (`data/checkpoints/step_0_layer0.json`).
- [ ] Task B: Ujednolicić format rekordu seed + writer JSON.
  - Skąd bierzemy kolejne punkty startowe: po standaryzacji zapis do `data/raw/<category>/...`; `checkpoint_input` następnego kroku wskazuje konkretny plik `data/raw/drivers/drivers_seed_v1.json`.
- [ ] Task C: Dodać pierwszy pionowy slice end-to-end dla `drivers` z checkpointem wejścia do kolejnego kroku.
  - Skąd bierzemy kolejne punkty startowe: `data/checkpoints/step_1_layer1_drivers.json` (URL-e kierowców po L0) -> wejście do kolejnego kroku L1.


## Etap 0.5 — Ujednolicenie struktury domen parserów (NOWE)
- [x] Dodać spójny podział katalogów domenowych: `list/`, `sections/`, `infobox/`, `postprocess/`.
- [x] Wydzielić logikę sekcyjną z parserów single/list do `sections/` (driver results, grand prix by year, season adapters: calendar/results/standings).
- [x] Wprowadzić wspólny interfejs parsera sekcyjnego (`SectionParseResult`, `SectionParser`).
- [x] Dodać mapę `DOMAIN_CRITICAL_SECTIONS` (`section_id`, `alternative_section_ids`) i użyć jej jako fallbacku w parserach GP.
- [ ] Migrować kolejne parsery domenowe (constructors/circuits) na nowy interfejs sekcyjny.

## Strumień C — Podział projektu na wcześniej powstałe części (stabilizacja architektury)
- [x] C1. Domknąć mapę odpowiedzialności modułów: `list/` (seed), `sections/` (body), `infobox/` (structured core), `postprocess/` (normalizacja domenowa).
  - Kontekst: dodano dokument granic modułów z mapą odpowiedzialności i regułami przepływu.
- [x] C2. Wymusić regułę importów: moduły `sections/` nie odwołują się do `single_scraper.py`; komunikacja wyłącznie przez serwisy/adaptory.
  - Kontekst: dodano test regresyjny skanujący importy we wszystkich domenach sekcyjnych.
- [x] C3. Dodać dokument „granice modułów” z przykładami przepływu danych dla każdej domeny (`drivers`, `constructors`, `circuits`, `seasons`, `grands_prix`).
  - Kontekst: nowy dokument `docs/MODULE_BOUNDARIES.md` z przykładami flow 0→1 i użyciem adaptera sekcji.
- [x] C4. Wprowadzić checklistę Definition of Done dla każdego nowego parsera sekcji (test snapshotowy + mapowanie aliasów + walidacja kontraktu + wpis w README domeny).
  - Kontekst: checklista DoD została osadzona w dokumencie granic modułów jako standard wejścia do code review, a testy sekcji korzystają ze wspólnego template'u fixture + expected records + metadata assertions.
- [x] C5. Przenieść wspólne helpery czyszczenia treści wiki do jednego modułu współdzielonego (`scrapers/wiki/parsers/elements/*`), aby uniknąć duplikacji domenowej.
  - Kontekst: dodano `text_cleaning.py` i podłączono parsery elementów oraz parser tabel.

## Kryteria ukończenia planu sekcyjnego
- [x] C6. Dodać meta-test CI wykrywający nowy moduł `scrapers/*/sections/*.py` bez aktualizacji coverage snapshot/contract.
  - Kontekst: `tests/test_section_parser_ci_meta.py` porównuje listę modułów sekcji z jawnie utrzymywaną macierzą coverage testów.
- [ ] Każda domena ma co najmniej 3 parsery sekcji działające przez wspólny adapter i wspólny kontrakt wynikowy.
- [x] Każda krytyczna sekcja z `DOMAIN_CRITICAL_SECTIONS` ma fallback aliasów i test regresyjny.
  - Kontekst: rozszerzono aliasy fallback dla `seasons` i `circuits` oraz dodano test obecności aliasów dla wszystkich domen.
- [x] Każdy parser sekcji ma przypisanie do jednej warstwy (`list`/`sections`/`infobox`/`postprocess`) bez mieszania odpowiedzialności.
  - Kontekst: granice warstw zostały zdefiniowane i spięte testem reguły importów dla `sections/`.

## Strumień D — OOP/DRY hardening
- [ ] D1. Wspólna baza `Complete*Extractor` dla domenowych extractorów complete (używanych w L0/L1) z kontraktem rozszerzeń per domena.
  - Metryka wejściowa: liczba zduplikowanych bloków logiki w `*complete*extractor*.py` + suma LOC extractorów complete (baseline z raportu duplikacji i LOC).
  - Metryka wyjściowa: spadek liczby zduplikowanych bloków o min. 40% oraz spadek LOC w extractorach complete o min. 20% bez utraty pokrycia testami kontraktowymi.
  - Kryterium ukończenia: istnieje wspólna klasa bazowa + co najmniej 3 domeny przepięte na nią + test regresyjny kontraktu extractora complete.
  - Skąd bierzemy kolejne punkty startowe: lista kandydatów do refaktoru pochodzi z raportu duplikacji (`scripts/analysis/duplication_report.md`) i z aktualnych kroków `data/checkpoints/step_*_layer*.json`, które wskazują najczęściej używane extractory.
- [ ] D2. Strategia resolverów URL (`UrlResolverStrategy`) zamiast domenowych if-else/fallbacków rozproszonych po parserach.
  - Metryka wejściowa: liczba miejsc w kodzie, gdzie URL jest składany/normalizowany inline (baseline: grep po `resolve`, `urljoin`, `wikipedia.org/wiki`).
  - Metryka wyjściowa: 100% budowania URL dla parserów L0/L1 przechodzi przez strategię + redukcja duplikacji resolverów o min. 50%.
  - Kryterium ukończenia: zarejestrowane strategie per domena, jeden punkt wejścia resolvera i testy regresyjne dla aliasów/relative URL/fallback.
  - Skąd bierzemy kolejne punkty startowe: źródła URL do migracji bierzemy z `checkpoint_input` aktywnych kroków orchestratora (pliki `data/checkpoints/*.json`) oraz z listy parserów wskazanych przez registry kroków 0/1.
- [x] D3. Centralizacja CLI i deprecated launcherów w jednym entrypoincie (z mapą kompatybilności i deprecations).
  - Metryka wejściowa: liczba aktywnych skryptów uruchomieniowych/entrypointów CLI + liczba zduplikowanych opcji uruchomieniowych.
  - Metryka wyjściowa: jeden canonical launcher + max 2 cienkie wrappery legacy, redukcja duplikowanych flag CLI o min. 60%.
  - Kryterium ukończenia: dokumentowana mapa `old_command -> new_command`, warning deprecacyjny w wrapperach i przejście smoke-testów uruchomienia dla przepływu L0/L1.
  - Kontekst: dodano canonical launcher `scrapers/cli.py`, cienkie wrappery delegujące w modułach z `__main__`, spójny `DeprecationWarning` i test statyczny pilnujący granic bootstrapów CLI.
  - Skąd bierzemy kolejne punkty startowe: priorytetowe komendy do migracji wyznaczamy z logów użycia CI/dev scripts i z kroków uruchamianych przez orchestrator `step_registry`.
- [ ] D4. Automatyzacja registry factory (auto-discovery parserów/extractorów/strategii zamiast ręcznej rejestracji).
  - Metryka wejściowa: liczba ręcznych wpisów w registry/factory + liczba incydentów „zapomniano zarejestrować komponent”.
  - Metryka wyjściowa: min. 80% wpisów generowanych automatycznie (konwencja + metadane), 0 incydentów brakującej rejestracji przez 2 kolejne iteracje.
  - Kryterium ukończenia: generator/rejestr auto-discovery działa dla parserów L0/L1, ma walidację konfliktów nazw i test CI blokujący niejawne komponenty.
  - Skąd bierzemy kolejne punkty startowe: backlog komponentów do auto-rejestracji budujemy z aktualnego `step_registry` i listy modułów domenowych używanych przez checkpointy iteracyjne.
- [ ] D5. Zasada mikro-refactoru w każdym PR funkcjonalnym jako merge gate.
  - Definicja: każdy PR funkcjonalny zawiera co najmniej 1 mikro-refactor redukujący duplikację lub wzmacniający kontrakt OOP.
  - Kryterium ukończenia: szablon PR wymusza sekcję „Refactor included”, a review blokuje merge PR bez tej sekcji.
  - Skąd bierzemy kolejne punkty startowe: kandydatów do mikro-refactoru bierzemy z bieżącego diffu PR i z raportu duplikacji (`scripts/analysis/duplication_report.md`).
- [ ] D6. Metryka trendu duplikacji per sprint (`removed_duplication` / `added_duplication`).
  - Definicja metryki: dla każdego sprintu raportujemy bilans `usunięto - dodano` (linie/bloki duplikacji) oraz trend kroczący z 3 sprintów.
  - Kryterium ukończenia: istnieje tabela trendu w dokumentacji i jest aktualizowana przy zamknięciu każdego sprintu.
  - Skąd bierzemy kolejne punkty startowe: dane wejściowe z sekcji „Refactor included” w PR oraz z wyników CI/static gates.
- [ ] D7. Przegląd sprintowy efektów refaktoryzacji i aktualizacja priorytetów backlogu D1-D6.
  - Cadence: 1x na sprint podczas review technicznego.
  - Kryterium ukończenia: po każdym sprincie istnieje notatka decyzji z listą „keep / increase / deprioritize” dla zadań refaktorowych.
  - Skąd bierzemy kolejne punkty startowe: trend metryki D6 + incydenty jakościowe z ostatniego sprintu.

## Cadence operacyjny (refactor governance)
- Każdy PR funkcjonalny: obowiązkowo sekcja „Refactor included” i minimum jeden mikro-refactor.
- Każdy sprint: podsumowanie metryki trendu duplikacji (`removed`/`added`) oraz decyzja o aktualizacji priorytetów refaktorów.
- Raz na kwartał: rewizja progów jakości (np. minimalny bilans netto i progi duplicate-code w CI).

## Skonsolidowany backlog wykrytych obszarów (layers / scrapers/base / validation / discovery / scripts/ci)

> Źródła punktów startowych backlogu: luki otwarte w etapach roadmapy (`Etap 1-4`, `D1-D7`), dług typowania z `docs/TYPING_GUARDRAILS.md`, oraz obszary techniczne wskazane w wizji/UML (orchestrator, walidacja regułowa, auto-discovery, redukcja duplikacji).

### Fala 1 — Quick wins (1 sprint)

| ID | Problem | Moduł | Expected impact | Owner | Deadline | Metryki sukcesu |
|---|---|---|---|---|---|---|
| QW-1 | Brak spójnego minimalnego schematu seed (`name`, `link`, `source_url`, `scraped_at`) utrudnia stabilne checkpointy L0→L1. | `layers.seed.*`, `scrapers/base/export/*` | Stabilniejsze wejście orchestratora i mniej regresji mapowania rekordów. | Data Platform (L0) | Sprint 1 (do 2026-04-12) | 100% seed scraperów zapisuje wymagane pola; 0 błędów kontraktu w testach seed registry. |
| QW-2 | Brak wspólnego logowania jakości (liczba rekordów, puste pola, duplikaty) per uruchomienie. | `layers/zero/*`, `validation/quality_stats.py`, `scrapers/base/results.py` | Szybka diagnostyka jakości danych i krótszy feedback loop w CI. | Data Quality | Sprint 1 (do 2026-04-12) | Raport jakości generowany dla każdego joba L0; metryki `record_count`, `empty_ratio`, `duplicates_count` obecne w 100% runów smoke CI. |
| QW-3 | Dług typowania (`Any`) utrzymuje się w krytycznym scope `layers/` i `validation/`. | `layers/seed/*`, `layers/zero/*`, `validation/*` | Wyższa stabilność refaktoru i mniej błędów kontraktowych w runtime. | Typing Guild | Sprint 1 (do 2026-04-12) | Redukcja wystąpień `Any` o min. 20% w wskazanych modułach; brak wzrostu błędów `mypy_regression_gate`; 0 nowych naruszeń `ANY-JUSTIFIED`. |
| QW-4 | Utility CI używają luźnych typów (`Any`) i rozproszonego formatowania raportów. | `scripts/ci/io_utils.py`, `scripts/ci/reporting.py`, `scripts/ci/git_diff.py` | Lepsza czytelność gate’ów i mniejsze ryzyko błędów narzędzi CI. | DevEx / CI | Sprint 1 (do 2026-04-12) | Redukcja `Any` o min. 50% w `scripts/ci/*`; 100% testów `tests/test_ci_utilities.py` przechodzi; jednolity format komunikatów błędów. |

### Fala 2 — Średnie (2–3 sprinty)

| ID | Problem | Moduł | Expected impact | Owner | Deadline | Metryki sukcesu |
|---|---|---|---|---|---|---|
| MID-1 | Brak jawnego `StepOrchestrator` dla flow `L0 -> L1 -> L0/L1` z deklaratywnym `checkpoint_input`. | `layers/orchestration/*`, `scrapers/base/orchestration/*` | Powtarzalny pipeline iteracyjny i pełna kontrola „skąd bierzemy kolejne punkty startowe”. | Pipeline Core | Sprint 3 (do 2026-05-10) | 100% kroków w `step_registry` ma `input->parser->output`; min. 1 e2e flow dla `drivers` i `constructors`; brak ręcznego wskazywania źródeł poza rejestrem. |
| MID-2 | Strategia URL resolverów nadal częściowo rozproszona między parserami. | `scrapers/base/helpers/url.py`, `scrapers/wiki/discovery.py`, domenowe list/single scrapers | Mniej duplikacji i spójne canonical URL dla L0/L1. | Scraper Core | Sprint 3 (do 2026-05-10) | 100% budowania URL przez wspólną strategię; redukcja duplikacji resolverów o min. 50%; testy alias/relative/fallback zielone. |
| MID-3 | Część parserów/komponentów discovery ma rejestrację ręczną zamiast kontrolowanego auto-discovery. | `scrapers/wiki/discovery.py`, `layers/orchestration/factories.py` | Krótszy onboarding nowych domen i mniej incydentów „zapomnianej rejestracji”. | Platform Architecture | Sprint 3 (do 2026-05-10) | Min. 80% komponentów parser/extractor rejestrowanych automatycznie; 0 incydentów brakującej rejestracji przez 2 sprinty. |
| MID-4 | Warstwa `scrapers/base` nadal ma obszary o mieszanej odpowiedzialności i duplikacji helperów. | `scrapers/base/helpers/*`, `scrapers/base/transformers/*`, `scrapers/base/mixins/*` | Uproszczenie API bazowego i łatwiejsze testowanie modułów bazowych. | Refactor Crew | Sprint 2-3 (do 2026-05-10) | Spadek duplikacji bloków o min. 30% (wg CI duplicate report); uproszczenie public API (min. 3 moduły z mniejszą liczbą punktów wejścia). |
| MID-5 | Walidacja działa, ale jest częściowo rozproszona między schematami/rules i validatorami domenowymi. | `validation/schema_engine.py`, `validation/schema_rules.py`, `validation/composite_validator.py` | Jednolity silnik reguł i mniejszy koszt utrzymania walidatorów. | Data Quality | Sprint 3 (do 2026-05-10) | Min. 40% reguł walidacyjnych przeniesionych do wspólnego engine; redukcja duplikatów reguł w domenach; brak regresji w `tests/test_validators*.py`. |

### Fala 3 — Strategiczne (4+ sprintów)

| ID | Problem | Moduł | Expected impact | Owner | Deadline | Metryki sukcesu |
|---|---|---|---|---|---|---|
| STR-1 | Brak pełnej wspólnej bazy `Complete*Extractor` dla domen L0/L1. | `scrapers/*/complete_scraper.py`, `scrapers/base/*` | Niższy koszt rozwijania nowych domen i mocniejsze kontrakty OOP/DRY. | Platform Architecture | Sprint 5+ (target: 2026-06-07) | Redukcja zduplikowanych bloków logicznych o min. 40%; spadek LOC extractorów complete o min. 20%; min. 3 domeny przepięte na wspólną bazę. |
| STR-2 | Brak pełnego domknięcia strict typing dla etapów 2–4 (`layers`, `validation`) i utrzymywanie wyjątków `ignore_errors`. | `mypy.ini`, `layers/*`, `validation/*` | Wyższa przewidywalność zmian i mniej błędów integracyjnych w pipeline. | Typing Guild | Sprint 6+ (target: 2026-06-21) | Usunięcie 100% `ignore_errors=True` dla etapów 2–4; 0 błędów mypy w scope; trwała redukcja `Any` do granic I/O. |
| STR-3 | Brak trendu refaktoryzacji jako metryki zarządczej sprint→sprint (`removed_duplication` vs `added_duplication`). | `scripts/ci/duplicate_report.py`, dokumentacja roadmapy/DoD | Governance techniczny: decyzje backlogowe oparte na danych, nie intuicji. | Engineering Manager + DevEx | Sprint 6+ (target: 2026-06-21) | Raport trendu 3-sprintowego publikowany co sprint; dodatni bilans netto duplikacji przez min. 3 sprinty z rzędu; 100% PR ma sekcję „Refactor included”. |
| STR-4 | Warstwa discovery i orkiestracji nadal wymaga ręcznych korekt przy rozszerzaniu nowych domen. | `scrapers/wiki/discovery.py`, `layers/application.py`, `layers/pipeline.py` | Skalowalne dodawanie domen (mniej kodu integracyjnego per nowy scraper). | Pipeline Core | Sprint 7+ (target: 2026-07-05) | Czas integracji nowej domeny skrócony o min. 50%; max 1 plik integracyjny wymagający ręcznej zmiany; uproszczenie API inicjalizacji pipeline (jedno wejście konfiguracyjne). |

### Kolejność realizacji i punkty startowe (jawnie)
- Fala 1 startuje z otwartych pozycji: Etap 1 (schema seed + quality logging), Etap 4 (metryki), rollout typowania (`docs/TYPING_GUARDRAILS.md`), oraz narzędzia `scripts/ci/*`.
- Fala 2 bierze input z rejestru kroków i checkpointów (`data/checkpoints/*.json`) + backlogu D1-D4 (orchestrator, URL strategy, auto-discovery).
- Fala 3 domyka długi strukturalne (wspólna baza extractorów, pełne strict typing, governance trendów duplikacji, skalowanie discovery).
