# ADR-0004: Zasady nazewnictwa hooków

- **Status:** Accepted
- **Data:** 2026-03-28
- **Autor:** zespół F1 parser
- **Decydenci:** maintainers domen i warstw pipeline
- **Dotyczy:** hooki lifecycle, extensibility points, callbacki parserów

## Kontekst
Hooki były nazywane niejednolicie (`before_*`, `pre_*`, `on_*`, `handle_*`), co utrudniało odnajdywanie punktów rozszerzeń i utrzymanie konwencji w wielu modułach.

## Decyzja
Wprowadzamy spójne nazewnictwo hooków:
- `before_<akcja>`: hook wykonywany przed akcją.
- `after_<akcja>`: hook wykonywany po akcji.
- `on_<zdarzenie>`: hook reaktywny na zdarzenie domenowe.
- `validate_<kontekst>`: hook walidacyjny.

Dodatkowo:
- Hook musi mieć pojedynczą odpowiedzialność i nazwę odzwierciedlającą fazę pipeline.
- Nie tworzymy nowych aliasów semantycznie równoważnych (`pre_`, `post_`) poza legacy-kompatybilnością.

## Konsekwencje
- Plusy:
  - Czytelniejszy lifecycle i szybszy onboarding.
  - Spójność nazewnicza między modułami.
- Minusy / trade-offy:
  - Potrzeba migracji istniejących nazw przy większych refaktorach.
- Ryzyka:
  - Krótkoterminowe duplikacje podczas okresu przejściowego.

## Weryfikacja
- Review blokuje nowe hooki spoza konwencji.
- Zmiany nazw hooków wymagają aktualizacji dokumentacji i referencji ADR.
