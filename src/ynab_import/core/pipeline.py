"""Conversion pipeline for processing transaction files."""

import logging
from pathlib import Path

import pandas as pd

from ynab_import.core.clean_input import clean_data_with_preset
from ynab_import.core.data_converter import convert_to_ynab
from ynab_import.core.preset import Preset
from ynab_import.file_rw.readers import read_transaction_file
from ynab_import.file_rw.writers import write_transactions_csv

logger = logging.getLogger(__name__)


def convert_file_with_preset(
    input_file: Path, preset: Preset, output_dir: Path, output_name: str
) -> Path:
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
        raise

    # Step 2: Clean the data according to preset rules
    try:
        # Only set header if we're skipping header rows
        should_set_header = preset.header_skiprows > 0
        cleaned_data = clean_data_with_preset(
            raw_data, preset, set_header=should_set_header
        )
        logger.debug(f"Cleaned data to {len(cleaned_data)} rows")
        logger.debug(f"Cleaned data columns: {list(cleaned_data.columns)}")
    except Exception as e:
        logger.error(f"Failed to clean data: {e}")
        raise

    # Step 3: Convert to YNAB format
    try:
        ynab_data = convert_to_ynab(cleaned_data, preset)
        logger.debug(f"Converted to YNAB format with {len(ynab_data.columns)} columns")
    except Exception as e:
        logger.error(f"Failed to convert to YNAB format: {e}")
        raise

    # Step 4: Write the output file
    try:
        if ynab_data.empty:
            raise ValueError(
                f"Converted data is empty. Check preset configuration for '{preset.name}'"
            )

        output_path = write_transactions_csv(ynab_data, output_dir, output_name)
        logger.info(f"Successfully converted file saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")
        raise


def preview_conversion(
    data: pd.DataFrame, preset: Preset, set_header: bool = True
) -> pd.DataFrame:
    """Preview what the conversion would look like without saving.

    Args:
        data: Raw transaction data
        preset: Preset configuration to use
        set_header: Whether to set first row as header after cleaning

    Returns:
        DataFrame showing the preview of converted data
    """
    try:
        # Clean the data
        cleaned_data = clean_data_with_preset(data, preset, set_header=set_header)

        # Convert to YNAB format
        ynab_data = convert_to_ynab(cleaned_data, preset)

        return ynab_data
    except Exception as e:
        logger.error(f"Failed to generate preview: {e}")
        raise
