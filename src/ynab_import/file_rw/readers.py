import csv
import json
from pathlib import Path

import pandas as pd

from ynab_import.core.preset import Preset


def read_transaction_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        with open(path) as file:
            # Read a sample to detect separator
            sample = file.read(1024)
            file.seek(0)

            # Try to detect separator
            sniffer = csv.Sniffer()
            try:
                delimiter = sniffer.sniff(sample).delimiter
            except csv.Error:
                # Try common delimiters if detection fails
                if ";" in sample:
                    delimiter = ";"
                else:
                    delimiter = ","  # fallback to comma

            return pd.read_csv(file, sep=delimiter)

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
