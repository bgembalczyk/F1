# Normalizacja pustych wartości

W warstwie `scrapers.base` obowiązuje jedna polityka obsługi pustych danych,
zdefiniowana w `scrapers/base/normalization.py` jako `EmptyValuePolicy`.

## Polityka `EmptyValuePolicy`

Polityka steruje tym, co dzieje się z pustymi wartościami:

- `EmptyValuePolicy.NORMALIZE` — zamienia puste wartości na `None`:
  - puste stringi (`""`, `"   "`) → `None`
  - puste listy i słowniki (`[]`, `{}`) → `None`
- `EmptyValuePolicy.KEEP` — pozostawia wartości bez zmian.

## Gdzie jest używana

- **`RecordNormalizer`** (`scrapers/base/normalization.py`)
  - używa `empty_value_policy` lub flagi `normalize_empty_values`.
  - normalizuje rekordy przed mapowaniem do kontraktów.
- **`RecordTransformer`** (`scrapers/base/transformers/record_transformer.py`)
  - posiada `empty_value_policy` oraz metodę `normalize_record()`,
    wykorzystywaną przez transformatory.
- **Fabryki rekordów**
  - `RecordFactoryTransformer` normalizuje rekordy przed wywołaniem fabryki.
  - `TablePipeline` normalizuje rekordy przed inicjalizacją modeli.

## Przykłady

```python
from scrapers.base.normalization import EmptyValuePolicy, RecordNormalizer

normalizer = RecordNormalizer(
    normalize_empty_values=False,
    empty_value_policy=EmptyValuePolicy.KEEP,
)
```

```python
from scrapers.base.transformers.record_factory import RecordFactoryTransformer
from scrapers.base.normalization import EmptyValuePolicy

transformer = RecordFactoryTransformer(
    record_factory=my_factory,
    empty_value_policy=EmptyValuePolicy.NORMALIZE,
)
```
