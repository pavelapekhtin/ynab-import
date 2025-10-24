"""File writing utilities for transaction data and preset configurations."""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from ynab_import.core.preset import Preset


def _generate_unique_filename(output_path: Path, base_filename: str) -> Path:
    """Generate a unique filename by adding numbers if file already exists."""
    file_path = output_path / base_filename

    if not file_path.exists():
        return file_path

    # Extract name and extension
    stem = file_path.stem
    suffix = file_path.suffix

    counter = 1
    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_file_path = output_path / new_filename
        if not new_file_path.exists():
            return new_file_path
        counter += 1


def write_transactions_csv(df: pd.DataFrame, output_path: Path, name: str) -> Path:
    """Write transaction DataFrame to CSV file with timestamped filename."""
    if df.empty:
        raise ValueError("DataFrame cannot be empty")

    if not name.strip():
        raise ValueError("Name cannot be empty")

    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    if not output_path.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {output_path}")

    # Generate filename with current date in dd-mm-yy format
    current_date = datetime.now().strftime("%d-%m-%y")
    base_filename = f"{name.strip()}_{current_date}.csv"

    # Generate unique filename to avoid overwriting
    file_path = _generate_unique_filename(output_path, base_filename)

    # Write DataFrame to CSV
    df.to_csv(file_path, index=False, encoding="utf-8")

    return file_path


def write_presets_json(output_path: Path, presets: dict[str, Preset]) -> Path:
    """Write presets dictionary to JSON file."""
    if not presets:
        raise ValueError("Presets dictionary cannot be empty")

    # Validate all values are Preset objects
    for key, preset in presets.items():
        if not isinstance(preset, Preset):
            raise TypeError(f"Value for key '{key}' is not a Preset object")

    # Ensure parent directory exists
    parent_dir = output_path.parent
    if not parent_dir.exists():
        raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    # Convert Preset objects to dictionaries for JSON serialization
    presets_data = {}
    for preset_key, preset in presets.items():
        presets_data[preset_key] = {
            "name": preset.name,
            "column_mappings": preset.column_mappings,
            "header_skiprows": preset.header_skiprows,
            "footer_skiprows": preset.footer_skiprows,
            "del_rows_with": preset.del_rows_with,
        }

    # Write to JSON file with proper formatting
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(presets_data, file, indent=2, ensure_ascii=False)

    return output_path
