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
## v0.4.0 (2025-10-24)

### Feat

- prevent file overwrite with automatic numbering

## v0.3.1 (2025-09-19)

### Fix

- **tests**: update config directory references for package rename

## v0.3.0 (2025-09-19)

### BREAKING CHANGE

- CLI command changed from 'ynab-import' to 'ynab-converter'

### Feat

- rename package from ynab-import to ynab-converter

## v0.2.11 (2025-09-19)

### Fix

- **ci**: restructure workflows for tag-based CI and release pipeline

## v0.2.10 (2025-09-19)

### Fix

- **tests**: replace MockPreset with real Preset instances for type compatibility

## v0.2.9 (2025-09-19)

### Fix

- **ci**: restore pyright type checking and resolve dependency issues

## v0.2.8 (2025-09-19)

### Fix

- **ci**: restore pyright type checking and resolve dependency issues

## v0.2.8 (2025-09-19)

### Fix

- remove problematic release workflow

## v0.2.7 (2025-09-19)

### Fix

- **ci**: remove testing for windows

## v0.2.6 (2025-09-19)

### Fix

- **tests**: make config tests platform agnostic

## v0.2.5 (2025-09-19)

### Fix

- **tests**: remove outdated tests

## v0.2.4 (2025-09-19)

### Fix

- **ci**: remove pyright from gh actions

## v0.2.3 (2025-09-19)

### Fix

- CI workflow triggers and linting issues

## v0.2.2 (2025-09-19)

### Fix

- **ci**: fix action trigger and ruff install

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
