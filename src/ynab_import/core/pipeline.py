"""Conversion pipeline for processing transaction files."""

import logging
from pathlib import Path

import pandas as pd

from ynab_import.core.clean_input import clean_data_pipeline
from ynab_import.core.data_converter import AmountParseError, convert_to_ynab
from ynab_import.core.diagnostics import (
    ConversionError,
    ConversionResult,
    PreviewResult,
    dataframe_excerpt,
)
from ynab_import.core.header_detection import prepare_data_for_conversion
from ynab_import.core.preset import Preset
from ynab_import.file_rw.readers import read_transaction_file
from ynab_import.file_rw.writers import write_transactions_csv

logger = logging.getLogger(__name__)


def convert_file_with_preset(
    input_file: Path, preset: Preset, output_dir: Path, output_name: str
) -> ConversionResult:
    """Convert a transaction file using a preset configuration.

    Args:
        input_file: Path to the input transaction file
        preset: Preset configuration to use for conversion
        output_dir: Directory where to save the converted file
        output_name: Base name for the output file

    Returns:
        Path to the created output file

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file format is not supported
        PermissionError: If unable to write output file
    """
    logger.info(f"Starting conversion of {input_file} with preset '{preset.name}'")

    # Step 1: Read the input file
    try:
        raw_data = read_transaction_file(input_file)
        logger.debug(f"Read {len(raw_data)} rows from {input_file}")
        logger.debug(f"Raw data columns: {list(raw_data.columns)}")
    except Exception as e:
        logger.error(f"Failed to read input file {input_file}: {e}")
        raise ConversionError(
            stage="read",
            summary="Failed to read the source transaction file.",
            expected="A readable CSV or Excel file with a tabular transaction export.",
            actual=str(e),
            preset_name=preset.name,
        ) from e

    header_preparation = prepare_data_for_conversion(raw_data, preset)

    # Step 2: Clean the data according to preset rules
    try:
        cleaned_data = clean_data_pipeline(
            header_preparation.data,
            header_rows=header_preparation.header_skiprows,
            footer_rows=header_preparation.footer_skiprows,
            del_rows_with=preset.del_rows_with,
            set_header=header_preparation.set_header,
        )
        logger.debug(f"Cleaned data to {len(cleaned_data)} rows")
        logger.debug(f"Cleaned data columns: {list(cleaned_data.columns)}")
    except Exception as e:
        logger.error(f"Failed to clean data: {e}")
        raise ConversionError(
            stage="clean",
            summary="Failed while cleaning rows before conversion.",
            expected="The preset cleaning rules should produce a usable transaction table.",
            actual=str(e),
            preset_name=preset.name,
            excerpt=dataframe_excerpt(raw_data),
        ) from e

    # Step 3: Convert to YNAB format
    try:
        ynab_data = convert_to_ynab(cleaned_data, preset)
        logger.debug(f"Converted to YNAB format with {len(ynab_data.columns)} columns")
    except AmountParseError as e:
        logger.error(f"Failed to parse amount value: {e}")
        relevant_columns = [e.column]
        raise ConversionError(
            stage="convert",
            summary="Failed to parse one of the mapped amount values.",
            expected=(
                "Mapped amount columns should contain numbers or common locale-formatted "
                "amount strings such as 1,234.56 or 1.234,56."
            ),
            actual=str(e),
            columns=relevant_columns,
            preset_name=preset.name,
            excerpt=dataframe_excerpt(cleaned_data, columns=relevant_columns),
        ) from e
    except Exception as e:
        logger.error(f"Failed to convert to YNAB format: {e}")
        raise ConversionError(
            stage="convert",
            summary="Failed to map cleaned data into YNAB columns.",
            expected="Mapped preset columns should exist and produce a non-empty YNAB-shaped table.",
            actual=str(e),
            columns=list(preset.column_mappings.values()),
            preset_name=preset.name,
            excerpt=dataframe_excerpt(
                cleaned_data, columns=list(preset.column_mappings.values())
            ),
        ) from e

    # Step 4: Write the output file
    try:
        if ynab_data.empty:
            raise ConversionError(
                stage="write",
                summary="Converted data is empty, so no CSV was written.",
                expected="At least one transaction row should remain after cleaning and conversion.",
                actual=f"Converted data is empty for preset '{preset.name}'.",
                preset_name=preset.name,
                excerpt=dataframe_excerpt(cleaned_data),
            )

        output_path = write_transactions_csv(ynab_data, output_dir, output_name)
        logger.info(f"Successfully converted file saved to {output_path}")
        return ConversionResult(
            output_path=output_path,
            warnings=header_preparation.warnings,
        )
    except ConversionError:
        raise
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")
        raise ConversionError(
            stage="write",
            summary="Failed to write the converted CSV output.",
            expected="A writable export directory and non-empty converted data.",
            actual=str(e),
            preset_name=preset.name,
            excerpt=dataframe_excerpt(ynab_data) if "ynab_data" in locals() else [],
        ) from e


def preview_conversion(
    data: pd.DataFrame, preset: Preset, set_header: bool | None = None
) -> PreviewResult:
    """Preview what the conversion would look like without saving.

    Args:
        data: Raw transaction data
        preset: Preset configuration to use
        set_header: Whether to set first row as header after cleaning.
            When None, use the preset/header-detection strategy.

    Returns:
        DataFrame showing the preview of converted data
    """
    try:
        header_preparation = prepare_data_for_conversion(data, preset)
        effective_set_header = (
            header_preparation.set_header if set_header is None else set_header
        )
        cleaned_data = clean_data_pipeline(
            header_preparation.data,
            header_rows=header_preparation.header_skiprows,
            footer_rows=header_preparation.footer_skiprows,
            del_rows_with=preset.del_rows_with,
            set_header=effective_set_header,
        )
        ynab_data = convert_to_ynab(cleaned_data, preset)
        return PreviewResult(data=ynab_data, warnings=header_preparation.warnings)
    except ConversionError:
        raise
    except AmountParseError as e:
        logger.error(f"Failed to generate preview: {e}")
        raise ConversionError(
            stage="convert",
            summary="Failed to parse one of the mapped amount values while generating the preview.",
            expected=(
                "Mapped amount columns should contain numbers or common locale-formatted "
                "amount strings such as 1,234.56 or 1.234,56."
            ),
            actual=str(e),
            columns=[e.column],
            preset_name=preset.name,
        ) from e
    except Exception as e:
        logger.error(f"Failed to generate preview: {e}")
        raise ConversionError(
            stage="convert",
            summary="Failed to generate the YNAB preview for this preset.",
            expected="Cleaning and mapped columns should produce a previewable YNAB table.",
            actual=str(e),
            columns=list(preset.column_mappings.values()),
            preset_name=preset.name,
        ) from e
