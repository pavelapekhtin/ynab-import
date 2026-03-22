# YNAB Import Tool

[![PyPI version](https://badge.fury.io/py/ynab-converter.svg)](https://badge.fury.io/py/ynab-converter)
[![Python versions](https://img.shields.io/pypi/pyversions/ynab-converter.svg)](https://pypi.org/project/ynab-converter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/ynab-converter?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/ynab-converter)

A command-line tool for converting bank export files (CSV, Excel) to YNAB-compatible CSV format.

## What it does

- Converts bank transaction files to YNAB's required CSV format
- Supports CSV and Excel files (.csv, .xlsx, .xls)
- Interactive terminal interface for file conversion
- Saves conversion settings as reusable presets
- Preview data before conversion
- Parses common locale-specific amount formats such as `1,234.56`, `1.234,56`, and accounting negatives
- Can auto-detect header rows for exports where the number of leading rows changes between files
- Shows richer conversion errors with stage-specific details and relevant data excerpts

## Installation

```bash
pip install ynab-converter
```

## Quick Start

1. Run the tool:
   ```bash
   ynab-converter
   ```

2. Create a preset using a sample file from your bank
3. Convert your bank files using the preset
4. Import the generated CSV into YNAB

## How it works

### Creating a preset

When you first run the tool, you'll create a preset for your bank's file format:

1. **Select a sample file** - Choose a transaction file from your bank
2. **Preview the data** - See how your file looks
3. **Choose header handling** - Use a fixed number of skipped rows or let the preset auto-detect the header row each time
4. **Clean up data** - Remove footer rows and unwanted summary rows if needed
5. **Map columns** - Tell the tool which columns contain:
   - Date
   - Payee/Description
   - Amount (or separate Inflow/Outflow columns)
   - Memo (optional)

### Converting files

Once you have a preset:
1. Select "Convert File"
2. Choose your transaction file
3. The tool reads, cleans, validates, and converts your file
4. If conversion fails, the CLI shows the failing stage, what was expected, and a compact excerpt of relevant data
5. The tool generates a YNAB-ready CSV file

## Smarter Parsing and Detection

### Amount parsing

The converter now normalizes common amount formats automatically, including:

- `1,234.56`
- `1.234,56`
- `1 234,56`
- values with currency symbols
- negative values written with `-` or parentheses, for example `($123.45)`

This applies both to:

- one signed amount column mapped to both `Inflow` and `Outflow`
- separate `Inflow` and `Outflow` columns stored as strings

### Header auto-detection

For exports where the number of rows before the table changes between files, presets can now use an auto-detect header mode:

- the converter looks for the row that best matches the mapped source column names
- if detection succeeds, that row becomes the header row for conversion
- if detection cannot confidently identify the header, the preset falls back to its saved header skip count and warns you

### Richer diagnostics

When a preset fails during preview or conversion, the CLI now tries to show:

- which stage failed (`read`, `clean`, `convert`, or `write`)
- what the converter expected
- the actual problem it saw
- the relevant mapped columns
- a small data excerpt to help you spot formatting or header issues quickly

## File Support

| Format | Extensions | Notes |
|--------|------------|-------|
| CSV    | `.csv`     | Auto-detects separators |
| Excel  | `.xlsx`, `.xls` | Reads first sheet |

## Platform Compatibility

**Supported platforms:**
- **macOS** (tested on macOS 15)
- **Linux** (tested on Ubuntu and other distributions)

**Not supported:**
- Windows (not tested, may have compatibility issues)

## Requirements

- Python 3.12+

## Configuration

Settings and presets are saved in:
- **Config**: `~/.config/ynab-converter/config.toml`
- **Presets**: `~/.config/ynab-converter/presets/presets.json`
- **Output**: `~/Downloads/ynab-exports/` (default)

Presets now also store how headers should be handled:

- fixed skipped-row mode
- auto-detect mode with saved fallback skip count

## Development

```bash
git clone https://github.com/pavelapekhtin/ynab-import.git
cd ynab-import
uv sync --dev
```

Run tests:
```bash
uv run pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/pavelapekhtin/ynab-import/issues)
- 📖 **Documentation**: This README

---

*Note: This tool is not affiliated with YNAB (You Need A Budget). It's an independent utility to help convert bank files to YNAB's CSV format.*
