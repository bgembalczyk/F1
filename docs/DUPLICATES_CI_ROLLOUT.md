# Stopniowe zaostrzanie progów duplikacji w CI

Workflow `static-quality-gates.yml` wykorzystuje `jscpd` dla **plików Python zmienionych w PR**, a następnie filtruje wynik do duplikatów dotykających **linii dodanych w danym PR**. Dzięki temu na starcie nie blokujemy merge przez dług historyczny, a jednocześnie nie dopuszczamy do dokładania nowych duplikatów.

## Aktualna konfiguracja (etap startowy)

Zmienne środowiskowe w workflow:

- `NEW_DUPLICATES_WARN_THRESHOLD=1` — od 1 nowego duplikatu pojawia się ostrzeżenie.
- `NEW_DUPLICATES_FAIL_THRESHOLD=3` — od 3 nowych duplikatów pipeline jest blokowany.

Każdy PR otrzymuje komentarz z listą duplikatów (plik + zakres linii + fragment kodu).

## Proponowany harmonogram zaostrzania

1. **Etap 1 (1-2 tygodnie)**
   - Obserwacja liczby ostrzeżeń.
   - Edukacja zespołu na podstawie komentarzy PR.
2. **Etap 2**
   - Obniżenie progu blokującego do `2`.
3. **Etap 3**
   - Ustawienie `WARN=0`, `FAIL=1` (każdy nowy duplikat blokuje).
4. **Etap 4 (docelowo)**
   - Rozszerzenie skanu na większy zakres (np. cały moduł lub cały repo), gdy dług historyczny zostanie zredukowany.

## Jak zmienić progi

W pliku `.github/workflows/static-quality-gates.yml` zaktualizuj wartości:

- `NEW_DUPLICATES_WARN_THRESHOLD`
- `NEW_DUPLICATES_FAIL_THRESHOLD`

Nie trzeba zmieniać skryptu raportującego — progi są przekazywane jako argumenty CLI.
