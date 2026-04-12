from __future__ import annotations

import importlib
import inspect
import pkgutil

import scrapers


def _required_init_params(parser_type: type) -> list[inspect.Parameter]:
    signature = inspect.signature(parser_type)
    return [
        parameter
        for parameter in signature.parameters.values()
        if parameter.name != "self"
        and parameter.default is inspect.Parameter.empty
        and parameter.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }
    ]


def _discover_contract_targets() -> list[tuple[str, type]]:
    targets: list[tuple[str, type]] = []

    for module_info in pkgutil.walk_packages(scrapers.__path__, prefix="scrapers."):
        module_name = module_info.name
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        for _, parser_type in inspect.getmembers(module, inspect.isclass):
            if parser_type.__module__ != module_name:
                continue
            if not parser_type.__name__.endswith("Parser"):
                continue
            if inspect.isabstract(parser_type):
                continue
            if _required_init_params(parser_type):
                continue
            targets.append((module_name, parser_type))

    return sorted(targets, key=lambda item: f"{item[0]}.{item[1].__name__}")


def _has_concrete_parse_provider(parser_type: type) -> bool:
    for base in parser_type.__mro__:
        parse = base.__dict__.get("parse")
        if parse is None:
            continue
        if getattr(parse, "__isabstractmethod__", False):
            continue
        return True
    return False


def test_non_abc_parsers_are_instantiable_and_parse_capable() -> None:
    targets = _discover_contract_targets()
    qualified_names = {f"{module}.{parser_type.__name__}" for module, parser_type in targets}

    assert "scrapers.parsers.wiki.table.WikiTableParser" in qualified_names

    failures: list[str] = []
    for module_name, parser_type in targets:
        qualified_name = f"{module_name}.{parser_type.__name__}"
        try:
            instance = parser_type()
        except Exception as exc:
            failures.append(f"{qualified_name}: cannot instantiate ({exc!r})")
            continue

        if not _has_concrete_parse_provider(parser_type):
            failures.append(f"{qualified_name}: no concrete parse provider in MRO")
            continue

        if not callable(getattr(instance, "parse", None)):
            failures.append(f"{qualified_name}: parse attribute is not callable")

    assert not failures, "\n".join(failures)
