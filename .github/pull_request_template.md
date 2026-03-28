## Opis zmiany

<!-- Krótko: co i dlaczego zostało zmienione -->

## Checklist (quality gate)

- [ ] **SRP**: każdy nowy/zmieniony komponent ma jedną, spójną odpowiedzialność.
- [ ] **DIP**: moduły wysokiego poziomu zależą od abstrakcji, nie od implementacji.
- [ ] **Brak nowej duplikacji**: sprawdzone lokalnie (`pylint` duplicate-code / CI static gates).
- [ ] **Zgodność z bazowymi abstrakcjami**: klasy rozszerzają istniejące kontrakty/interfejsy i nie łamią ich API.
