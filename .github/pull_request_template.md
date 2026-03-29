## Opis zmiany

<!-- Krótko: co i dlaczego zostało zmienione. -->

## Checklist (quality gate)

- [ ] **SRP**: każdy nowy/zmieniony komponent ma jedną, spójną odpowiedzialność.
- [ ] **DIP**: moduły wysokiego poziomu zależą od abstrakcji, nie od implementacji.
- [ ] **Brak nowej duplikacji**: sprawdzone lokalnie (`pylint` duplicate-code / CI static gates).
- [ ] **Zgodność z bazowymi abstrakcjami**: klasy rozszerzają istniejące kontrakty/interfejsy i nie łamią ich API.
- [ ] Brak nowych `Any`.
- [ ] Granice modułów.
- [ ] Duplikacja.
- [ ] Architecture impact.

## Architecture impact

- Zmiany w `scrapers/base/`: <!-- opisz konkretnie, nie wpisuj "nie dotyczy" gdy PR modyfikuje ten obszar -->
- Dotknięte domeny: <!-- np. scrapers, layers, infrastructure -->
- Kompatybilność wsteczna: <!-- np. zachowana / breaking + opis -->
- Migracja wymagana: <!-- tak/nie + opis jeśli tak -->

## Refactor included

<!-- Wymagane dla każdego PR funkcjonalnego: minimum 1 mikro-refactor redukujący duplikację lub wzmacniający kontrakt OOP. -->

- [ ] Mikro-refactor wykonany (redukcja duplikacji **lub** poprawa kontraktu OOP).
- Typ: <!-- np. DRY / OOP contract -->
- Zakres (pliki/moduły): <!-- krótko -->
- Wpływ na duplikację (linie lub bloki): **usunięto:** <!-- n --> / **dodano:** <!-- n -->
- Notatka o kompatybilności kontraktu: <!-- np. brak zmian API / opis zmian -->
