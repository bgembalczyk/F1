# scrapers/base/factory — README techniczne

## Odpowiedzialność
- Moduły pomocnicze do składania scraperów bazowych i adapterów runtime.

## Publiczne API
- Brak stabilnego API dla zewnętrznych pakietów (`__all__ = []`).

## Co jest internal
- Wszystkie moduły w katalogu (np. `runtime_factory.py`, `adapter_chain.py`).

## Zasady użycia
- Domena scrapera korzysta z wyższych warstw (`scrapers.base.*`), nie importuje bezpośrednio głębokich modułów factory, jeśli nie jest to konieczne.
