#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import sys
from typing import Any

from scrapers.base.infobox.dsl import InfoboxSchemaDSL
from scrapers.base.infobox.schema import InfoboxSchema
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL


def _load_target(target: str) -> Any:
    if ":" not in target:
        msg = "Target must be in module:attribute form."
        raise ValueError(msg)
    module_path, attr = target.split(":", 1)
    module = importlib.import_module(module_path)
    obj = getattr(module, attr)
    if hasattr(obj, "CONFIG"):
        return obj.CONFIG
    return obj


def _convert_to_dsl(obj: Any) -> dict[str, Any]:
    if isinstance(obj, ScraperConfig):
        return TableSchemaDSL.from_config(obj).to_dict()
    if isinstance(obj, InfoboxSchema):
        return InfoboxSchemaDSL.from_schema(obj).to_dict()
    msg = (
        "Unsupported target. Provide a ScraperConfig, InfoboxSchema, "
        "or a class/module exposing CONFIG."
    )
    raise TypeError(
        msg,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert scraper configs or infobox schemas to DSL JSON.",
    )
    parser.add_argument(
        "target",
        help="Target in module:attribute format (e.g. scrapers.drivers.list_scraper:F1DriversListScraper).",
    )
    args = parser.parse_args()
    try:
        obj = _load_target(args.target)
        payload = _convert_to_dsl(obj)
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
