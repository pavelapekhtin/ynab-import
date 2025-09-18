# YNAB Import Tool

[![PyPI version](https://badge.fury.io/py/ynab-import.svg)](https://badge.fury.io/py/ynab-import)
[![Python versions](https://img.shields.io/pypi/pyversions/ynab-import.svg)](https://pypi.org/project/ynab-import/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A command-line tool for converting bank export files (CSV, Excel) to YNAB-compatible CSV format.

## What it does

- Converts bank transaction files to YNAB's required CSV format
- Supports CSV and Excel files (.csv, .xlsx, .xls)
- Interactive terminal interface for file conversion
- Saves conversion settings as reusable presets
- Preview data before conversion

## Installation

```bash
pip install ynab-import
```

## Quick Start

1. Run the tool:
   ```bash
   ynab-import
   ```

2. Create a preset using a sample file from your bank
3. Convert your bank files using the preset
4. Import the generated CSV into YNAB

## How it works

### Creating a preset

When you first run the tool, you'll create a preset for your bank's file format:

1. **Select a sample file** - Choose a transaction file from your bank
2. **Preview the data** - See how your file looks
3. **Clean up data** - Remove header/footer rows if needed
4. **Map columns** - Tell the tool which columns contain:
   - Date
   - Payee/Description  
   - Amount (or separate Inflow/Outflow columns)
   - Memo (optional)

### Converting files

Once you have a preset:
1. Select "Convert File"
2. Choose your transaction file
3. The tool generates a YNAB-ready CSV file

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
- **Config**: `~/.config/ynab-import/config.toml`
- **Presets**: `~/.config/ynab-import/presets/presets.json`
- **Output**: `~/Downloads/ynab-exports/` (default)

## Development

```bash
git clone https://github.com/pavelapekhtin/ynab-import.git
cd ynab-import
uv sync --dev
```

Run tests:
```bash
pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/pavelapekhtin/ynab-import/issues)
- 📖 **Documentation**: This README

---

*Note: This tool is not affiliated with YNAB (You Need A Budget). It's an independent utility to help convert bank files to YNAB's CSV format.*