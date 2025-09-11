# Bank Statement to YNAB Converter - Specification

**Version**: 1.0
**Date**: 2024-01-XX
**Status**: Draft

## Overview

A command-line tool that converts bank statement files (CSV and Excel formats) from various banks into YNAB-compatible CSV format. The tool supports custom format definitions, field mapping, and provides a beautiful terminal interface using Rich/Textual.

## User Stories

### Primary User Stories

**US001: Convert Bank Statements**
- As a YNAB user
- I want to convert my bank statement files (CSV/Excel) to YNAB format
- So that I can import my transactions without manual data entry

**US002: Handle Different Bank Formats**
- As a user with accounts from multiple banks
- I want the tool to recognize different column structures and naming conventions
- So that I can convert statements regardless of bank-specific formatting

**US003: Custom Format Configuration**
- As a power user
- I want to create and save custom format definitions for my banks
- So that I can handle new banks or format changes without code modifications

**US004: Command-Line Operation**
- As a terminal user on Mac/Linux
- I want to run conversions via command line with file path input
- So that I can integrate the tool into scripts and workflows

### Supporting User Stories

**US005: Data Validation**
- As a user
- I want to see validation errors and warnings during conversion
- So that I can identify and fix data quality issues

**US006: Custom Field Mapping**
- As a user with unique requirements
- I want to customize how bank fields map to YNAB fields
- So that I can handle edge cases in my specific bank statements

**US007: Interactive Terminal Experience**
- As a terminal user
- I want to navigate the tool using arrow keys and selections
- So that I have a beautiful and intuitive user experience

## Acceptance Criteria

### AC001: File Format Support
- ✅ Tool accepts CSV files as input
- ✅ Tool accepts Excel files (.xlsx, .xls) as input
- ✅ Tool produces YNAB-compatible CSV output with columns: Date, Payee, Memo, Inflow, Outflow
- ✅ Output dates are in YYYY-MM-DD format

### AC002: Column Structure Flexibility
- ✅ Tool handles varying column names (e.g., "Description" vs "Transaction Description")
- ✅ Tool processes single amount columns with positive/negative values
- ✅ Tool processes separate debit/credit columns
- ✅ Tool ignores irrelevant columns automatically

### AC003: Command Line Interface
- ✅ Tool runs on Mac and Linux terminals
- ✅ Tool accepts file path as command line argument
- ✅ Tool outputs converted file to specified or default location
- ✅ Tool provides clear success/error messages
- ✅ Tool supports interactive mode with arrow key navigation
- ✅ Tool uses Rich library for beautiful terminal output

### AC004: Format Configuration
- ✅ Tool supports configurable format definitions stored in TOML files
- ✅ Users can create new format definitions without code changes
- ✅ Tool can auto-detect format based on column headers
- ✅ Users can specify format explicitly via command line flag

### AC005: Data Transformation
- ✅ Tool converts various date formats to YYYY-MM-DD
- ✅ Tool extracts payee information from transaction descriptions
- ✅ Tool handles memo field population from available data
- ✅ Tool correctly maps amounts to Inflow/Outflow columns

### AC006: Error Handling
- ✅ Tool validates input file exists and is readable
- ✅ Tool reports parsing errors with line numbers
- ✅ Tool handles missing required columns gracefully
- ✅ Tool validates date formats and reports conversion issues

## Success Metrics

### Functional Success
- **Conversion Accuracy**: 100% of valid transactions converted correctly
- **Format Coverage**: Supports 95%+ of common bank statement variations
- **Error Detection**: Identifies and reports 100% of data validation issues

### Usability Success
- **Setup Time**: New format definition created in <5 minutes
- **Processing Speed**: Converts 1000 transactions in <10 seconds
- **Error Clarity**: All error messages actionable by end user

### Technical Success
- **Platform Compatibility**: Runs on Mac and Linux without additional dependencies
- **File Size Handling**: Processes files up to 10MB without memory issues
- **Configuration Flexibility**: New bank formats added via config files only

## Edge Cases

### File Structure Edge Cases
- **Empty files**: Files with headers only or completely empty
- **Malformed CSV**: Files with inconsistent column counts
- **Mixed encodings**: Files with non-UTF-8 encoding
- **Large files**: Files exceeding typical memory constraints

### Data Quality Edge Cases
- **Missing dates**: Transactions without date information
- **Invalid dates**: Unparseable or impossible dates (e.g., Feb 30)
- **Missing amounts**: Transactions without amount information
- **Zero amounts**: Transactions with $0.00 amounts
- **Extreme amounts**: Very large or very small transaction amounts

### Format Variation Edge Cases
- **Header variations**: Different capitalization, spacing, punctuation
- **Amount representations**: Various currency symbols, decimal separators
- **Date format variations**: Different date formats within same file
- **Multi-line descriptions**: Transaction descriptions spanning multiple rows

### Configuration Edge Cases
- **Invalid format definitions**: Malformed configuration files
- **Conflicting formats**: Multiple formats matching same file structure
- **Missing format**: Files that don't match any defined format

## Non-Functional Requirements

### Performance Requirements
- **Processing Speed**: Convert 1000 transactions in ≤10 seconds
- **Memory Usage**: Process files up to 10MB with ≤100MB RAM usage
- **Startup Time**: Tool initialization in ≤2 seconds

### Reliability Requirements
- **Data Integrity**: Zero data loss during conversion
- **Error Recovery**: Graceful handling of all invalid input scenarios
- **Consistency**: Identical output for identical input across runs

### Usability Requirements
- **Documentation**: Complete usage examples and format definition guide
- **Error Messages**: Clear, actionable error descriptions
- **Configuration**: Human-readable configuration file format (TOML)
- **Terminal Experience**: Rich formatting and interactive navigation

### Maintainability Requirements
- **Modularity**: Separate modules for parsing, transformation, and output
- **Extensibility**: New formats added via configuration, not code
- **Testing**: Comprehensive test suite with sample files from multiple banks

### Security Requirements
- **Local Processing**: All processing occurs locally, no network transmission
- **File Permissions**: Respects system file permissions and access controls
- **Data Cleanup**: No sensitive data retained after processing

## Technical Constraints

### Platform Constraints
- **Operating Systems**: Mac OS X 10.15+, Linux (Ubuntu 18.04+, similar)
- **Architecture**: x64 and ARM64 support required
- **Dependencies**: Minimal external dependencies for easy installation

### Format Constraints
- **Input Formats**: CSV (RFC 4180 compliant), Excel (.xlsx, .xls)
- **Output Format**: CSV with specific YNAB column structure
- **Configuration Format**: TOML for format definitions

### Processing Constraints
- **File Size**: Maximum 10MB input files
- **Transaction Count**: Maximum 50,000 transactions per file
- **Memory Footprint**: Maximum 100MB RAM usage during processing

## YNAB Output Format Specification

The tool must produce CSV files with exactly these columns in this order:

```csv
Date,Payee,Memo,Inflow,Outflow
2024-01-15,Amazon.com,Online purchase,0.00,45.67
2024-01-16,Salary Deposit,Monthly salary,3500.00,0.00
```

### Column Specifications
- **Date**: YYYY-MM-DD format (ISO 8601)
- **Payee**: Extracted from transaction description, cleaned of extraneous data
- **Memo**: Additional transaction details, optional
- **Inflow**: Positive amounts (income, deposits) with 2 decimal places
- **Outflow**: Negative amounts (expenses, withdrawals) with 2 decimal places, stored as positive values

## Questions for Further Clarification

[NEEDS CLARIFICATION]
1. **Default output location**: Should converted files be saved in same directory as input, or specific output directory?
2. **File naming**: What naming convention for output files? (e.g., `original_name_ynab.csv`)
3. **Payee extraction rules**: Any specific patterns for cleaning up payee names from descriptions?
4. **Amount precision**: How many decimal places should be preserved in amount fields?
5. **Configuration location**: Where should format definition files be stored? User home directory?

## Traceability Matrix

| Requirement ID | User Story | Acceptance Criteria | Success Metric |
|---------------|------------|-------------------|----------------|
| REQ001 | US001 | AC001, AC005 | Conversion Accuracy |
| REQ002 | US002 | AC002, AC004 | Format Coverage |
| REQ003 | US003 | AC004 | Configuration Flexibility |
| REQ004 | US004 | AC003 | Platform Compatibility |
| REQ005 | US005 | AC006 | Error Detection |
| REQ006 | US006 | AC004, AC005 | Configuration Flexibility |
| REQ007 | US007 | AC003 | Error Clarity |

---

**Specification Status**: Ready for Implementation Plan
**Next Step**: Generate detailed implementation plan with technical architecture
