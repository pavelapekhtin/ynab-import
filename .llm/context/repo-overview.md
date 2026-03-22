# Repo Overview

## Purpose

`ynab-import` packages as `ynab-converter`, a terminal app that helps users convert bank export files (`.csv`, `.xlsx`, `.xls`) into YNAB-ready CSV files. The practical user goal is:

1. Create a reusable preset from one representative bank export.
2. Reuse that preset to convert later exports into YNAB columns.

## Primary Entry Points

- `src/ynab_import/cli/menus.py`
  The real application entrypoint. `main_menu()` handles `-v/--version`, then launches the interactive Questionary/Rich menu flow.
- `pyproject.toml`
  Publishes the `ynab-converter` console script pointing to `ynab_import.cli.menus:main_menu`.
- `main.py`
  Thin local wrapper that calls `main_menu()`.
- `run_cli.py`
  Dev convenience launcher that prepends `src/` to `sys.path` and runs `main_menu()`.

Treat `src/ynab_import/cli/menus.py` plus the console script in `pyproject.toml` as the canonical active path.

## Practical Architecture

### CLI layer

- `src/ynab_import/cli/menus.py`
  Interactive UX, file picking, preview tables, preset creation/deletion/selection, and config updates.
- `src/ynab_import/cli/ascii_art.py`
  Banner art only.

### Domain/core layer

- `src/ynab_import/core/preset.py`
  `Preset` dataclass. This is the persisted schema used across the app.
- `src/ynab_import/core/config.py`
  User config and preset storage paths, load/save helpers, and config mutation helpers.
- `src/ynab_import/core/clean_input.py`
  Header/footer trimming, row deletion by text match, optional header promotion.
- `src/ynab_import/core/data_converter.py`
  Maps cleaned data into YNAB columns, normalizes locale-specific amount strings, splits a signed amount column when mapped to both `Inflow` and `Outflow`, formats dates, and drops unmapped columns.
- `src/ynab_import/core/header_detection.py`
  Detects likely header rows for presets using persisted auto-detect mode.
- `src/ynab_import/core/diagnostics.py`
  Structured conversion warnings/errors plus sanitized data excerpts for CLI reporting.
- `src/ynab_import/core/pipeline.py`
  Orchestrates read -> header strategy -> clean -> convert -> write, plus preview conversion with warnings and structured errors.

### File I/O layer

- `src/ynab_import/file_rw/readers.py`
  Reads CSV/Excel transaction files and preset JSON.
- `src/ynab_import/file_rw/writers.py`
  Writes timestamped CSV exports and preset JSON.

### Tests

- `tests/`
  Main executable spec for current behavior. The most important behavioral tests cover conversion, cleaning, config persistence, CSV diagnostics, and version handling.

## Current Realities Future Agents Might Miss

- This is a local desktop CLI, not a service or API-backed app.
- User state lives outside the repo in the platform config dir from `platformdirs.user_config_dir("ynab-converter")`.
- Presets are stored as JSON and config as TOML. The app assumes both are user-editable artifacts.
- Presets can now use either fixed header skipping or persisted auto-detect header mode with fallback.
- The conversion flow is intentionally tolerant of messy CSV input and falls back to lenient parsing before giving a diagnostic error.
- The UI supports choosing either separate inflow/outflow columns or a single signed amount column.
- Amount columns may arrive as locale-formatted strings; normalization now happens in the core conversion layer rather than being left to pandas defaults.
- `README.md` mentions YNAB CSV output generally; the code is the source of truth for exact column ordering and transformations.

## Implementation Notes

- Python package root is `src/ynab_import`.
- The repo includes release workflow docs (`WORKFLOW_GUIDE.md`, `PUBLISHING_CHECKLIST.md`) and Commitizen config in `pyproject.toml`.
- There is no existing repo-local agent context system other than `BOOTSTRAP_LLM_PROMPT.md`; `.llm/` is now the source of truth for future agents.
