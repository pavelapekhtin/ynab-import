# API Contracts

## Core Behavioral Contracts

### Preset schema is stable app data

`Preset` currently means:

- `name: str`
- `column_mappings: dict[str, str]`
- `header_skiprows: int`
- `footer_skiprows: int`
- `del_rows_with: list[str]`

This shape is serialized into `presets.json` and read back without schema migration. Any change here is a user-data compatibility change.

### Conversion pipeline contract

`convert_file_with_preset()` in `src/ynab_import/core/pipeline.py` performs these steps in order:

1. Read the source file.
2. Clean rows using preset rules.
3. Convert to YNAB columns.
4. Refuse to write empty converted output.
5. Write a timestamped CSV in the chosen export directory.

Do not reorder these steps casually; preset behavior and previews depend on this sequence.

### Cleaning semantics

Cleaning means:

- Remove `header_skiprows` rows from the top.
- Remove `footer_skiprows` rows from the bottom.
- Remove any row containing any string in `del_rows_with`.
- Optionally promote the first remaining row to column headers.

Text deletion is currently case-sensitive because it uses `str.contains()` with default case handling. Changing that would be user-visible.

### Column mapping semantics

Valid YNAB target columns in current code are:

- `Date`
- `Payee`
- `Memo`
- `Inflow`
- `Outflow`

Unmapped source columns are dropped from final output.

If both `Inflow` and `Outflow` map to the same source column, the app interprets that source as a signed amount column:

- positive values become `Inflow`
- negative values become absolute-value `Outflow`
- the original source column is removed after splitting

If only one of `Inflow` or `Outflow` maps to a source column, values pass through as-is even if signs look unusual.

### Output CSV contract

`write_transactions_csv()` currently guarantees:

- non-empty DataFrame required
- non-empty output name required
- export path must already exist and be a directory
- filename format is `{name}_{dd-mm-yy}.csv`
- collisions are resolved by appending `_1`, `_2`, etc.

Silently changing naming or overwrite behavior would affect user workflows and test expectations.

### Config and state locations

User state is stored under the platform config dir for `ynab-converter`:

- `config.toml`
- `presets/presets.json`

Current config keys are:

- `active_preset`
- `export_path`
- `input_folder`

`None` values are omitted from serialized TOML.

### CLI contract

The published CLI command is `ynab-converter`.

Non-interactive CLI behavior is minimal:

- `-v` / `--version` prints version and exits.

All other normal behavior is interactive menu-driven flow from `main_menu()`.

## Data and Domain Meaning

- The app does not categorize transactions for YNAB; it only reshapes bank exports into YNAB import columns.
- Presets represent bank-export format knowledge, not a specific account or budget.
- Preview behavior is important because users rely on it to validate header trimming and column mapping before conversion.
- CSV parsing is intentionally defensive because bank exports may include BOMs, semicolon delimiters, inconsistent lines, and malformed rows.

## What Must Not Change Silently

- Preset JSON shape.
- Config file keys and default export path behavior.
- Single-amount-column split semantics.
- Column order filtering to YNAB-relevant columns.
- Version flag behavior on the CLI.
- The app’s tolerance strategy for imperfect CSVs.

## Open Contracts / Pending Validation

- The exact YNAB import requirements are inferred from code and tests, not from an external formal spec in this repo.
- Windows support is described as untested rather than explicitly unsupported by code. Keep platform claims aligned with README and real testing evidence.
- The release workflow docs mention `main`/`staging` branch practices, but current local git history includes inconsistent historical commit messages. Treat Conventional Commits as the desired default, not a perfectly enforced historic reality.
