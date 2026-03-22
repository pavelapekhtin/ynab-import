# Tooling Rules

## Runtime and Packaging

- Python: `>=3.12`
- Build backend: `hatchling`
- Package name: `ynab-converter`
- Source layout: `src/`
- Primary dependency workflow: `uv`

## Main Commands

- Sync dev environment: `uv sync --dev`
- Run tests: `uv run pytest`
- Run a focused test file: `uv run pytest tests/test_data_converter.py`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type-check: `uv run pyright`
- Run CLI locally: `uv run ynab-converter`

## Practical Verification Habits

- For conversion logic changes, run at least:
  - `uv run pytest tests/test_data_converter.py tests/test_clean_input.py tests/test_csv_diagnostics.py`
- For config or persistence changes, run at least:
  - `uv run pytest tests/test_config.py tests/test_writers.py`
- For entrypoint/version changes, run at least:
  - `uv run pytest tests/test_version.py`
- For broad refactors, prefer the full suite:
  - `uv run pytest`
  - `uv run ruff check .`
  - `uv run pyright`

## Repo Quirks

- In some sandboxed environments, `uv run ...` may fail because `uv` tries to access a global cache outside the writable workspace. When that happens, use local environment binaries if present, for example `./.venv/bin/pytest`.
- This checkout already has tests that shell out to `uv run ynab-converter --version`; those integration tests can fail in restricted sandboxes even when the code is correct.
- `ruff` and `pyright` are configured in `pyproject.toml`, but local binaries may not exist unless dev dependencies were installed.
- `tests/` often prepend `src/` to `sys.path` directly; avoid “cleaning that up” unless you also update the test strategy consistently.

## File and Workflow Notes

- Entry script published to users is `ynab-converter`, not `python main.py`.
- Config and preset writes target the user config directory, not the repo.
- Manual CLI verification matters for menu-driven changes because passing tests does not exercise Rich/Questionary UX.
