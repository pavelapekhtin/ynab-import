import csv
import json
import logging
from pathlib import Path

import pandas as pd

from ynab_import.core.preset import Preset

logger = logging.getLogger(__name__)


def read_transaction_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        with open(path, encoding="utf-8-sig") as file:
            # Read a sample to detect separator
            sample = file.read(1024)
            file.seek(0)

            # Try to detect separator with improved logic
            delimiter = ","  # default

            # Count occurrences of common delimiters in the sample
            comma_count = sample.count(",")
            semicolon_count = sample.count(";")

            # Use the more frequent delimiter, with preference for semicolon if tied
            if semicolon_count > comma_count:
                delimiter = ";"
            elif semicolon_count > 0 and comma_count == 0:
                delimiter = ";"

            # Try CSV sniffer as secondary validation
            sniffer = csv.Sniffer()
            try:
                detected_delimiter = sniffer.sniff(sample).delimiter
                # If sniffer found something different and it's common, use it
                if (
                    detected_delimiter in [",", ";", "\t"]
                    and detected_delimiter in sample
                ):
                    delimiter = detected_delimiter
            except csv.Error:
                pass  # Keep our count-based detection

            # Try reading with pandas, handling common CSV issues
            try:
                return pd.read_csv(
                    file,
                    sep=delimiter,
                    encoding="utf-8-sig",
                    skipinitialspace=True,
                    quoting=csv.QUOTE_MINIMAL,
                )
            except pd.errors.ParserError as e:
                # If parsing fails, try with more lenient settings
                logger.warning(f"Initial CSV parsing failed: {e}")
                file.seek(0)

                try:
                    # Try with error handling and flexible field counting
                    return pd.read_csv(
                        file,
                        sep=delimiter,
                        encoding="utf-8-sig",
                        skipinitialspace=True,
                        quoting=csv.QUOTE_MINIMAL,
                        on_bad_lines="warn",  # Warn but continue processing
                        engine="python",  # Use Python engine for more flexibility
                    )
                except Exception:
                    # Last resort: try to read line by line and find the issue
                    file.seek(0)
                    lines = file.readlines()

                    # Analyze the structure to provide better error info
                    field_counts = []
                    for i, line in enumerate(lines[:20], 1):  # Check first 20 lines
                        if line.strip():  # Skip empty lines
                            # Count fields by splitting on delimiter
                            fields = len(line.split(delimiter))
                            field_counts.append((i, fields))

                    if field_counts:
                        most_common_count = max(
                            {count for _, count in field_counts},
                            key=lambda x: sum(1 for _, c in field_counts if c == x),
                        )
                        inconsistent_lines = [
                            (line_num, count)
                            for line_num, count in field_counts
                            if count != most_common_count
                        ]

                        error_msg = (
                            f"CSV file has inconsistent field counts. "
                            f"Expected {most_common_count} fields based on most common pattern, "
                            f"but found inconsistencies in lines: {inconsistent_lines[:5]}. "
                            f"Please check your CSV file for missing commas, unescaped quotes, "
                            f"or line breaks within fields."
                        )
                    else:
                        error_msg = f"Unable to parse CSV file: {e}"

                    raise ValueError(error_msg) from e

    elif path.suffix.lower() in [".xlsx", ".xls"]:
        with open(path, "rb") as file:
            return pd.read_excel(file)
    else:
        raise ValueError(
            f"Unsupported file format: {path.suffix}. Only CSV and Excel files are supported."
        )


def read_presets_file(path: Path) -> dict[str, Preset]:
    """Read presets from a JSON file and return as a dictionary of Preset objects."""
    with open(path, encoding="utf-8") as file:
        presets_data = json.load(file)

    presets = {}
    for preset_key, preset_config in presets_data.items():
        preset = Preset(
            name=preset_config["name"],
            column_mappings=preset_config["column_mappings"],
            header_skiprows=preset_config["header_skiprows"],
            footer_skiprows=preset_config["footer_skiprows"],
            del_rows_with=preset_config["del_rows_with"],
        )
        presets[preset_key] = preset

    return presets
