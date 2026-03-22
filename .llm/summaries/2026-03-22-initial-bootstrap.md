# Initial Bootstrap Summary

## Why This Exists

Created the repo-local `.llm/` context system so future LLM sessions can recover project context without relying on prior chat history.

## What Was Inferred

- The active app is an interactive Python CLI published as `ynab-converter`.
- The canonical flow is preset-driven: read file -> clean rows -> map/split columns -> write timestamped CSV.
- User state is stored outside the repo via platformdirs in TOML/JSON files.
- Tests are the strongest source of truth for conversion, cleaning, CSV tolerance, and version behavior.

## Important Continuation Files

- `src/ynab_import/cli/menus.py`
- `src/ynab_import/core/pipeline.py`
- `src/ynab_import/core/data_converter.py`
- `src/ynab_import/core/clean_input.py`
- `src/ynab_import/core/config.py`
- `src/ynab_import/file_rw/readers.py`
- `src/ynab_import/file_rw/writers.py`
- `pyproject.toml`
- `tests/test_data_converter.py`
- `tests/test_clean_input.py`
- `tests/test_config.py`
- `tests/test_csv_diagnostics.py`
- `tests/test_version.py`

## Unresolved Questions

- No formal YNAB external spec is stored in the repo, so output semantics are inferred from current code/tests.
- Release workflow docs describe a `staging` -> `main` process, but local history shows that commit style enforcement has not been perfectly consistent.
- Sandbox restrictions can make `uv run ...` verification fail even when code is fine; future sessions should distinguish environment failures from code regressions.
