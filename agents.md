# agents.md

## Instrukcja dla zadań planistycznych
Jeżeli otrzymujesz zadanie typu:
- „zaplanuj kolejne taski”,
- „zaktualizuj roadmapę”,
- „co dalej w projekcie?”,

to **najpierw** sprawdź i oprzyj się głównie na plikach:
1. `docs/FUTURE_VISION_DATASET_PIPELINE.md`
2. `docs/ROADMAP_TASKS_DATASET_ML.md`
3. `docs/uml_future_dataset_pipeline.puml`

## Sposób aktualizacji planu
- Aktualizuj status zadań przez checkboxy (`[ ]` / `[x]`) w `docs/ROADMAP_TASKS_DATASET_ML.md`.
- Jeśli coś zostało zrobione: odznacz jako wykonane (`[x]`) i dopisz krótki kontekst (co dokładnie domknięto).
- Jeśli pojawiają się nowe zależności: dopisz kolejne kroki w odpowiednim etapie roadmapy.
- Pilnuj spójności między roadmapą, wizją architektury i UML.
- W planowaniu iteracji zawsze dopisuj jawnie: **skąd bierzemy kolejne punkty startowe**.

## Priorytety
1. Najpierw domykanie fundamentów wiki-parserów i warstwy 0.
2. Potem warstwa 1 oraz iteracyjny orchestrator 0/1.
3. Na końcu przygotowanie pod tokenizację i encoding pod ML.

## Zasada dla poprawek po review
- Nie modyfikuj plików `*.json` przy poprawkach po komentarzach do PR.
- Zmiany wprowadzaj wyłącznie w plikach Python (`*.py`) oraz dokumentacji (`docs/`, `agents.md`).

