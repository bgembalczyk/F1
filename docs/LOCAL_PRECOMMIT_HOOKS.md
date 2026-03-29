# Lokalne hooki pre-commit (zamiast GitHub CI)

Repo używa autorskiego hooka `pre-commit`, który zastępuje dotychczasowe workflow po stronie GitHub Actions.

## Instalacja hooka

```bash
bash scripts/hooks/install-hooks.sh
```

Skrypt ustawia:

- `core.hooksPath=.githooks`
- aktywny hook: `.githooks/pre-commit`

## Ręczne uruchamianie bramek

```bash
bash scripts/local/run-precommit.sh
```

## Co sprawdza hook

1. `radon` (warning threshold od klasy `B`)
2. `xenon` (progi blokujące: `C/C/B`)
3. `pylint` (duplikacja + oversized jednostki)
4. `jscpd` na staged plikach `*.py` (progi `NEW_DUPLICATES_WARN_THRESHOLD`, `NEW_DUPLICATES_FAIL_THRESHOLD`)
5. `import-linter`
6. `mypy`
7. `pytest` dla kontraktów domenowych
8. `python scripts/check_known_module_typos.py`
9. `pytest` dla testów architektonicznych

## Wymagania lokalne

- Python 3.10+
- pakiety z `requirements-dev.txt`
- Node.js 20+ (`npx` do `jscpd`)
