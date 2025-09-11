# Bank Statement to YNAB Converter - Implementation Plan

**Version**: 1.0
**Date**: 2024-01-XX
**Status**: Draft
**Based on**: SPECIFICATION.md v1.0

## Architecture Overview

### Technology Stack
- **Language**: Python 3.12+
- **CLI Framework**: Rich + Textual for beautiful terminal interface with arrow navigation
- **Data Processing**: Pandas for CSV/Excel handling, Pydantic for validation
- **Project Management**: uv for dependency management
- **Testing**: pytest with sample bank statement fixtures
- **Configuration**: TOML for format definitions (human-readable)

### Architecture Decision Rationale

**Rich + Textual Choice**: Rich provides beautiful terminal output, while Textual enables full TUI applications with arrow navigation and selection menus, meeting the requirement for navigable terminal interface.

**Pandas Choice**: Industry standard for CSV/Excel processing, handles various formats and encodings robustly, essential for bank statement variations.

**Pydantic Choice**: Required by constraints, perfect for validating bank statement data and configuration schemas.

**TOML Configuration**: More human-readable than JSON, supports comments for documentation, preferred by user.

## Project Structure

```
ynab-import/
├── pyproject.toml              # uv project config, dependencies, tool configs
├── README.md                   # Installation and usage instructions
├── docs/
│   ├── specs/
│   │   ├── SPECIFICATION.md
│   │   └── IMPLEMENTATION_PLAN.md
│   └── examples/               # Usage examples and tutorials
├── config/
│   ├── formats/                # User-created format definitions (TOML)
│   │   └── .gitkeep            # Keep directory in version control
│   ├── templates/              # Format definition templates
│   │   └── basic_format.toml   # Template for creating new formats
│   └── schema.toml             # Configuration schema documentation
├── src/
│   └── ynab_import/
│       ├── __init__.py
│       ├── main.py             # CLI entry point
│       ├── models/
│       │   ├── __init__.py
│       │   ├── transaction.py  # Pydantic models for transactions
│       │   └── config.py       # Pydantic models for configuration
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── base.py         # Abstract base parser
│       │   ├── csv_parser.py   # CSV file parser
│       │   ├── excel_parser.py # Excel file parser
│       │   └── factory.py      # Parser factory for format detection
│       ├── converters/
│       │   ├── __init__.py
│       │   ├── ynab.py         # YNAB format converter
│       │   └── mapper.py       # Field mapping logic
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── tui.py          # Textual TUI application
│       │   ├── components.py   # Custom UI components
│       │   ├── preview.py      # File preview interface
│       │   └── mapper.py       # Column mapping interface
│       ├── config/
│       │   ├── __init__.py
│       │   ├── loader.py       # Configuration loading
│       │   └── validator.py    # Configuration validation
│       └── utils/
│           ├── __init__.py
│           ├── date_utils.py   # Date parsing utilities
│           ├── file_utils.py   # File handling utilities
│           └── exceptions.py   # Custom exceptions
├── tests/
│   ├── unit/
│   │   ├── test_parsers.py
│   │   ├── test_converters.py
│   │   ├── test_models.py
│   │   └── test_config.py
│   ├── integration/
│   │   └── test_full_conversion.py
│   ├── fixtures/
│   │   ├── sample_statements/
│   │   │   ├── generic_single_amount.csv
│   │   │   ├── generic_debit_credit.csv
│   │   │   └── generic_excel.xlsx
│   │   └── expected_outputs/
│   │       └── expected_ynab_output.csv
│   └── conftest.py             # pytest fixtures
└── sample_data/                # Sample files for development
```

## Phase Gates Analysis

### Simplicity Gate ✅
- **Single primary project**: One CLI tool with clear purpose
- **Minimal abstractions**: Direct parser → converter → output pipeline
- **Essential dependencies only**: Rich/Textual for UI, Pandas for data, Pydantic for validation

### Anti-Abstraction Gate ✅
- **Direct framework usage**: Using Pandas and Rich directly without wrapper layers
- **No premature generalization**: Format definitions handle variations, not complex inheritance hierarchies
- **Configuration over code**: New bank formats via TOML, not Python classes

### Integration-First Gate ✅
- **Clear contracts**: Pydantic models define interfaces between components
- **File-based I/O**: Standard input/output patterns for CLI tools
- **Testable components**: Each parser and converter independently testable

## Implementation Phases

### Phase 1: Core Data Models & Configuration (2-3 days)
**Deliverable**: Pydantic models and TOML configuration system

**Components**:
- `models/transaction.py`: BankTransaction and YnabTransaction models
- `models/config.py`: FormatDefinition and AppConfig models
- `config/loader.py`: TOML configuration loading
- `config/validator.py`: Configuration validation logic
- `utils/exceptions.py`: Custom exception hierarchy

**Key Features**:
- Type-safe transaction models with validation
- TOML-based format definitions with schema validation
- Comprehensive error handling for configuration issues
- Support for various amount column structures
- Template system for creating new format definitions

**Phase Gate Criteria**:
- All models pass Pydantic validation
- TOML configurations load and validate correctly
- Unit tests achieve 100% coverage for models
- Clear error messages for invalid configurations

### Phase 2: File Parsers & Format Detection (3-4 days)
**Deliverable**: CSV and Excel parsers with automatic format detection

**Components**:
- `parsers/base.py`: Abstract parser interface
- `parsers/csv_parser.py`: CSV file parsing with encoding detection
- `parsers/excel_parser.py`: Excel file parsing (.xlsx, .xls support)
- `parsers/factory.py`: Format detection and parser selection
- `utils/file_utils.py`: File handling utilities

**Key Features**:
- Automatic encoding detection for CSV files
- Support for both Excel formats (.xlsx, .xls)
- Header-based format detection
- Configurable skip rows and data cleaning
- Robust error handling for malformed files

**Phase Gate Criteria**:
- Successfully parse sample files from 5+ major banks
- Handle common file encoding issues (UTF-8, UTF-8-BOM, Windows-1252)
- Format detection accuracy >95% on test dataset
- Graceful handling of malformed files with clear error messages

### Phase 3: YNAB Conversion Logic (2-3 days)
**Deliverable**: Transaction conversion from bank format to YNAB format

**Components**:
- `converters/ynab.py`: Core YNAB conversion logic
- `converters/mapper.py`: Field mapping and transformation rules
- `utils/date_utils.py`: Date parsing and standardization

**Key Features**:
- Flexible date format parsing and standardization
- Intelligent payee extraction from transaction descriptions
- Amount normalization (single column vs. debit/credit columns)
- Memo field population from available data
- Data validation and error reporting
- Interactive preview of conversion results

**Phase Gate Criteria**:
- 100% accurate conversion for valid transactions
- Handles all common date formats encountered in bank statements
- Payee extraction rules work for major transaction types
- Clear validation errors for data quality issues

### Phase 4: Terminal User Interface (3-4 days)
**Deliverable**: Rich/Textual-based CLI with arrow key navigation

**Components**:
- `ui/tui.py`: Main Textual application
- `ui/components.py`: Custom UI components
- `main.py`: CLI entry point with Typer integration

**Key Features**:
- File browser with arrow key navigation
- Interactive file preview with sample data display
- Column mapping interface with drag-and-drop style selection
- Format creation wizard with step-by-step guidance
- Real-time conversion preview before processing
- Progress indicators for conversion process
- Error display with actionable messages
- Configuration management interface

**Phase Gate Criteria**:
- Intuitive navigation using arrow keys only
- Clear visual feedback for all user actions
- Responsive interface for files up to 10MB
- Comprehensive error handling with user-friendly messages

### Phase 5: CLI Integration & Final Testing (2-3 days)
**Deliverable**: Complete command-line interface with both direct and interactive modes

**Components**:
- Enhanced `main.py`: Complete CLI with all options
- Integration tests and end-to-end validation
- Documentation and usage examples

**Key Features**:
- Direct conversion mode for scripting
- Interactive mode with full TUI
- Comprehensive logging and progress reporting
- Configuration file management commands

**Phase Gate Criteria**:
- All acceptance criteria from specification validated
- Performance requirements met (1000 transactions <10 seconds)
- Complete test coverage including integration tests
- User documentation with examples

## Data Models & Schemas

### Transaction Models

```python
# Core transaction models structure
class BankTransaction(BaseModel):
    """Raw transaction from bank statement with flexible fields."""
    date: Optional[date] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    debit: Optional[Decimal] = None
    credit: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    reference: Optional[str] = None
    category: Optional[str] = None
    raw_data: dict[str, Any] = Field(default_factory=dict)

class YnabTransaction(BaseModel):
    """YNAB-formatted transaction with strict validation."""
    date: date = Field(..., description="Transaction date in YYYY-MM-DD format")
    payee: str = Field(..., min_length=1, description="Transaction payee")
    memo: str = Field(default="", description="Transaction memo")
    inflow: Decimal = Field(default=Decimal('0'), ge=0, description="Inflow amount")
    outflow: Decimal = Field(default=Decimal('0'), ge=0, description="Outflow amount")
```

### Configuration Schema

```toml
# Example format definition structure
[format_info]
name = "My Bank Format"
description = "Custom format created by user"
file_patterns = ["*.csv"]  # User can specify patterns

[parsing]
skip_rows = 0
encoding = "utf-8"  # Auto-detected during preview
has_header = true

[column_mappings]
# User selects these during interactive mapping
date = ""           # Column name from file
description = ""    # Column name from file
amount = ""         # Column name from file (if single column)
# OR for separate columns:
# debit = ""        # Column name from file
# credit = ""       # Column name from file

[date_processing]
input_format = ""   # Auto-detected or user-specified
output_format = "%Y-%m-%d"

[amount_processing]
handling = "single"  # User selects during setup: "single", "separate"
inflow_positive = true  # User configures based on their data
currency_symbol = "$"
decimal_places = 2

[payee_extraction]
# Simple extraction - use description field as-is initially
# User can add patterns later if needed
default_field = "description"
max_length = 50
cleanup_patterns = []  # User can add cleanup rules

[memo_processing]
source_fields = ["description"]  # User selects during setup
max_length = 200
```

## Testing Strategy

### Test Pyramid Structure

**Unit Tests (70%)**:
- Individual model validation
- Parser component testing
- Converter logic verification
- Configuration loading and validation

**Integration Tests (20%)**:
- End-to-end file conversion
- Multi-format processing
- Error handling scenarios
- Performance validation

**System Tests (10%)**:
- CLI interface testing
- TUI navigation testing
- Real-world file processing
- Cross-platform compatibility

### Test Data Management

**Sample Data Requirements**:
- Generic sample files with common column structures
- Various file formats and encoding types
- Edge cases: empty files, malformed data, extreme values
- Expected output files for validation
- User-provided real files during development for testing

**Property-Based Testing**:
- Use Hypothesis for generating edge case transactions
- Validate data integrity through conversion pipeline
- Test date parsing with random valid/invalid dates
- Amount handling with various decimal representations

## Dependencies & Configuration

### pyproject.toml Structure

```toml
[project]
name = "ynab-import"
version = "0.1.0"
description = "Convert bank statements to YNAB format with beautiful terminal interface"
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "your.email@example.com"}]

requires-python = ">=3.12"
dependencies = [
    "pandas>=2.0.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0",
    "textual>=0.40.0",
    "typer>=0.9.0",
    "openpyxl>=3.1.0",  # Excel support
    "toml>=0.10.0",     # TOML config files
    "chardet>=5.0.0",   # Encoding detection
    "python-dateutil>=2.8.0",  # Flexible date parsing
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "hypothesis>=6.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pre-commit>=3.0.0",
]

[project.scripts]
ynab-import = "ynab_import.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# Tool configurations
[tool.ruff]
line-length = 88
target-version = "py312"
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "W", "C90", "I", "N", "UP", "B", "A", "C4", "PIE", "SIM"]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.lint.isort]
known-first-party = ["ynab_import"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = [
    "--cov=src/ynab_import",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=85",
]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

## Error Handling Strategy

### Exception Hierarchy

```python
class YnabImportError(Exception):
    """Base exception for YNAB import errors."""

class FileFormatError(YnabImportError):
    """Raised when file format cannot be determined or parsed."""

class DataValidationError(YnabImportError):
    """Raised when transaction data fails validation."""

class ConfigurationError(YnabImportError):
    """Raised when configuration is invalid or missing."""

class ConversionError(YnabImportError):
    """Raised when conversion process fails."""
```

### Error Handling Principles

1. **Fail Fast**: Validate inputs early in the pipeline
2. **Clear Messages**: Every error includes actionable guidance
3. **Context Preservation**: Include file names, line numbers, field names
4. **Recovery Options**: Suggest fixes when possible
5. **Logging**: Comprehensive logging for debugging

## Performance Considerations

### Memory Management
- **Streaming Processing**: Process large files in chunks
- **Lazy Loading**: Load configurations only when needed
- **Memory Profiling**: Monitor memory usage during development

### Processing Optimization
- **Vectorized Operations**: Use pandas for bulk data transformations
- **Efficient Parsing**: Minimize string operations and regex usage
- **Caching**: Cache format detection results and compiled patterns

### Scalability Targets
- **File Size**: Handle files up to 10MB efficiently
- **Transaction Volume**: Process 50,000 transactions without performance degradation
- **Response Time**: UI interactions respond within 100ms

## Security Considerations

### Data Privacy
- **Local Processing**: All data processing occurs locally
- **No Network**: Tool operates entirely offline
- **Temporary Files**: Secure cleanup of temporary files
- **Memory Cleanup**: Clear sensitive data from memory after processing

### File System Security
- **Permission Checks**: Validate file permissions before processing
- **Path Validation**: Prevent directory traversal attacks
- **Safe Defaults**: Default to read-only operations where possible

## Implementation Timeline

### Week 1: Foundation (Phase 1)
- **Days 1-2**: Set up project structure, dependencies, and development environment
- **Days 3-4**: Implement core Pydantic models and TOML configuration system
- **Day 5**: Unit tests and configuration validation

### Week 2: Data Processing (Phases 2-3)
- **Days 1-3**: File parsers with format detection and encoding handling
- **Days 4-5**: YNAB conversion logic and field mapping

### Week 3: User Interface (Phase 4)
- **Days 1-3**: Textual TUI application with navigation
- **Days 4-5**: Rich CLI integration and progress indicators

### Week 4: Integration & Testing (Phase 5)
- **Days 1-2**: CLI integration and command-line options
- **Days 3-4**: Integration testing and performance validation
- **Day 5**: Documentation and final testing

## Risk Assessment & Mitigation

### High Risk Areas

**Risk**: Excel format variations across different banks
- **Mitigation**: Collect comprehensive sample data early
- **Fallback**: Graceful degradation with clear error messages

**Risk**: Date parsing complexity with international formats
- **Mitigation**: Use python-dateutil with format hints
- **Fallback**: Manual format specification in configuration

**Risk**: Memory usage with large files
- **Mitigation**: Implement streaming/chunked processing
- **Fallback**: File size validation with clear limits

**Risk**: Character encoding issues in CSV files
- **Mitigation**: Use chardet for automatic detection
- **Fallback**: Manual encoding specification option

### Medium Risk Areas

**Risk**: TUI performance on slower systems
- **Mitigation**: Optimize rendering and minimize redraws
- **Fallback**: Simple CLI mode for basic functionality

**Risk**: Configuration complexity overwhelming users
- **Mitigation**: Provide comprehensive examples and templates
- **Fallback**: Auto-detection covers most common cases

## Success Criteria

### Technical Success Criteria
- [ ] All unit tests pass with >85% coverage
- [ ] Integration tests validate end-to-end functionality
- [ ] Performance targets met for file size and transaction volume
- [ ] Cross-platform compatibility verified (Mac/Linux)

### User Experience Success Criteria
- [ ] New users can convert their first file in <2 minutes
- [ ] Format configuration completed in <5 minutes
- [ ] Error messages lead to successful resolution >90% of the time
- [ ] Terminal interface is intuitive for keyboard-only navigation

### Business Success Criteria
- [ ] User can configure any bank format through the UI
- [ ] Reduces manual transaction entry time by >90%
- [ ] Zero data loss during conversion process
- [ ] Format creation process is intuitive for non-technical users
- [ ] Preview interface clearly shows conversion results before processing

---

**Implementation Plan Status**: Ready for Phase 1 Development
**Next Step**: Begin Phase 1 implementation with core models and configuration system
