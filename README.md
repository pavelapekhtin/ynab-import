# YNAB Import Tool

A command-line tool for converting bank transaction files to YNAB-compatible CSV format.

## Features

- Interactive CLI with beautiful terminal interface
- Support for CSV and Excel files (.csv, .xlsx, .xls)
- Customizable presets for different bank formats
- Tab completion for file paths
- Real-time preview of data transformations
- Configurable data cleaning (header/footer removal, row filtering)
- Column mapping with sample data preview

## Installation

```bash
# Install dependencies
uv sync

# Or if using pip
pip install -e .
```

## Usage

### Run the CLI

```bash
# From project root
python run_cli.py

# Or directly
python src/ynab_import/cli/menus.py
```

### CLI Interface

The tool provides an interactive menu system with the following options:

1. **Convert File** - Convert a transaction file using the active preset
2. **Select Preset** - Choose from available presets
3. **Create Preset** - Interactively create a new preset using a sample file
4. **Delete Preset** - Remove existing presets
5. **Exit** - Quit the application

### Creating Presets

When creating a preset, you'll be guided through:

1. **Sample File Selection** - Choose a representative transaction file
2. **Data Preview** - View first 10 and last 3 rows of your file
3. **Header/Footer Configuration** - Specify rows to skip
4. **Row Filtering** - Define text patterns for row deletion
5. **Column Mapping** - Map your bank's columns to YNAB format:
   - Date
   - Payee
   - Memo
   - Inflow
   - Outflow

### Configuration

Configuration is automatically stored in:
- **Config**: `~/.config/ynab-import/config.toml`
- **Presets**: `~/.config/ynab-import/presets/presets.json`
- **Default Export**: `~/Downloads/ynab-exports/`

## File Format Support

- **CSV files**: Auto-detection of separators (comma, semicolon)
- **Excel files**: .xlsx and .xls formats
- **Output**: YNAB-compatible CSV with proper date formatting

## Requirements

- Python 3.12+
- Dependencies: pandas, rich, prompt-toolkit, simple-term-menu, pydantic

## Development

```bash
# Run tests
pytest

# Format code
ruff format

# Lint
ruff check
```
