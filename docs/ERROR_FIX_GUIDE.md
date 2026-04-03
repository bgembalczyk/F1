# Error fix guide

## `pipeline.parse_failed`
- Sprawdź, czy parser otrzymuje poprawny HTML i czy sekcja docelowa istnieje.
- Zweryfikuj selektory w `parse()` / `_parse_soup()`.

## `pipeline.normalize_failed`
- Upewnij się, że rekordy wejściowe zawierają wymagane pola.
- Sprawdź mapowanie nazw pól i typów przed normalizacją.

## `pipeline.transform_failed`
- Zweryfikuj transformery oraz kolejność ich wykonywania.
- Sprawdź, czy transformery nie zakładają brakujących kluczy.

## `pipeline.validate_failed`
- Przejrzyj reguły walidatora i dane wyjściowe z kroku `transform`.
- Sprawdź raport jakości walidacji zapisany dla runa.

## `pipeline.post_process_failed`
- Zweryfikuj post-processory i ich oczekiwane wejście.
- Sprawdź, czy operacje końcowe nie modyfikują rekordów in-place w sposób niezgodny z kontraktem.
