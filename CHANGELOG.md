# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### Added

- Initial release of YNAB Import Tool
- Interactive CLI with rich terminal interface
- Support for CSV and Excel file formats (.csv, .xlsx, .xls)
- Preset management system for bank-specific conversion rules
- Live data preview during preset creation
- Configurable data cleaning (header/footer removal, row filtering)
- Column mapping with sample data preview
- Tab completion for file path selection
- Automatic configuration file management
- YNAB-compatible CSV output format
- Beautiful ASCII art banner and color-themed interface
- Support for multiple date formats and currency representations
- Cross-platform compatibility (Windows, macOS, Linux)

### Features

- **Convert File**: Transform bank transaction files using saved presets
- **Select Preset**: Switch between different bank conversion configurations
- **Create Preset**: Interactive wizard for setting up new bank formats
- **Delete Preset**: Remove unwanted preset configurations
- **Data Preview**: View file structure before and after transformation
- **Smart Defaults**: Sensible default settings for common bank formats

### Technical

- Built with Python 3.12+ support
- Uses modern tools: Rich, Questionary, Pandas, Pydantic
- Follows PEP 621 project standards
- Comprehensive type annotations
- Modular architecture with clean separation of concerns
- Configuration stored in standard user directories
- Proper error handling and user feedback

### Configuration

- Config location: `~/.config/ynab-import/config.toml`
- Presets location: `~/.config/ynab-import/presets/presets.json`
- Default export path: `~/Downloads/ynab-exports/`

[Unreleased]: https://github.com/pavelapekhtin/ynab-import/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pavelapekhtin/ynab-import/releases/tag/v0.1.0
## v0.2.1 (2025-09-19)

### Fix

- **ci**: remove py3.13 testing

## v0.2.0 (2025-09-19)

### Feat

- make ready for pypi publishing
- make ready for pypi publishing
refactor(cli): fix linting errrors and tweak ui
- first working prototype

### Fix

- **ci**: api token name for pypi fixed
