import argparse
from pathlib import Path

from scrapers.wiki.application import create_default_wiki_pipeline_application


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wiki pipeline bootstrap CLI")
    parser.add_argument(
        "--mode",
        choices=("layer0", "layer1", "full"),
        default="layer0",
        help="Tryb uruchomienia pipeline'u wiki.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    app = create_default_wiki_pipeline_application(
        base_wiki_dir=Path("data/wiki").resolve(),
        base_debug_dir=Path("data/debug").resolve(),
    )

    if args.mode in {"layer0", "full"}:
        app.run_layer_zero()

    if args.mode in {"layer1", "full"}:
        app.run_layer_one()


if __name__ == "__main__":
    main()
