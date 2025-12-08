from __future__ import annotations

import argparse
import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Type

from scrapers.base.helpers import build_output_path
from scrapers.base.scraper import F1Scraper


def _is_scraper_class(obj: object) -> bool:
    return inspect.isclass(obj) and issubclass(obj, F1Scraper)


def _load_scraper_class(name: str) -> Type[F1Scraper]:
    """Znajdź klasę scrapera po nazwie lub pełnej ścieżce modułu."""

    if "." in name:
        module_name, class_name = name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        candidate = getattr(module, class_name, None)
        if _is_scraper_class(candidate):
            return candidate
        raise ValueError(f"{name} nie wskazuje na klasę scrapera")

    import scrapers

    for module_info in pkgutil.walk_packages(scrapers.__path__, f"{scrapers.__name__}."):
        module = importlib.import_module(module_info.name)
        candidate = getattr(module, name, None)
        if _is_scraper_class(candidate):
            return candidate

    raise ValueError(f"Nie znaleziono scrapera o nazwie '{name}'")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Uruchom wybraną klasę scrapera")
    parser.add_argument(
        "scraper",
        help="Nazwa klasy scrapera (np. F1DriversListScraper lub pełna ścieżka modułu)",
    )
    parser.add_argument(
        "--output-dir",
        default=Path("data/wiki"),
        type=Path,
        help="Katalog bazowy dla eksportu (domyślnie data/wiki)",
    )
    parser.add_argument(
        "--include-urls",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Czy dołączać URL-e w danych wynikowych",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    try:
        scraper_cls = _load_scraper_class(args.scraper)
    except Exception as exc:  # noqa: BLE001 - chcemy przekazać każdą informację dalej
        raise SystemExit(str(exc)) from exc

    scraper = scraper_cls(include_urls=args.include_urls)

    data = scraper.fetch()
    print(f"Pobrano rekordów: {len(data)}")

    json_path = build_output_path(scraper, args.output_dir, extension="json")
    csv_path = build_output_path(scraper, args.output_dir, extension="csv")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    scraper.to_json(json_path)
    scraper.to_csv(csv_path)

    print(f"Zapisano pliki:\n - {json_path}\n - {csv_path}")


if __name__ == "__main__":
    main()
