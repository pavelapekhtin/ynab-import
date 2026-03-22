from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
from pandas import DataFrame

from ynab_import.core.preset import Preset

logger = logging.getLogger(__name__)


def read_transaction_file(path: Path) -> DataFrame:
    if path.suffix.lower() == ".csv":
        with open(path, encoding="utf-8-sig") as file:
            sample = file.read(1024)
            file.seek(0)

            delimiter = ","

            comma_count = sample.count(",")
            semicolon_count = sample.count(";")

            if semicolon_count > comma_count:
                delimiter = ";"
            elif semicolon_count > 0 and comma_count == 0:
                delimiter = ";"

            sniffer = csv.Sniffer()
            try:
                detected_delimiter = sniffer.sniff(sample).delimiter
                if (
                    detected_delimiter in [",", ";", "\t"]
                    and detected_delimiter in sample
                ):
                    delimiter = detected_delimiter
            except csv.Error:
                pass

            try:
                return pd.read_csv(  # type: ignore[return-value]
                    file,
                    sep=delimiter,
                    encoding="utf-8-sig",
                    skipinitialspace=True,
                    quoting=csv.QUOTE_MINIMAL,
                )
            except pd.errors.ParserError as e:
                logger.warning(f"Initial CSV parsing failed: {e}")
                file.seek(0)

                try:
                    return pd.read_csv(  # type: ignore[return-value]
                        file,
                        sep=delimiter,
                        encoding="utf-8-sig",
                        skipinitialspace=True,
                        quoting=csv.QUOTE_MINIMAL,
                        on_bad_lines="warn",
                        engine="python",
                    )
                except Exception:
                    file.seek(0)
                    lines = file.readlines()

                    field_counts: list[tuple[int, int]] = []
                    for i, line in enumerate(lines[:20], 1):
                        if line.strip():
                            fields = len(line.split(delimiter))
                            field_counts.append((i, fields))

                    if field_counts:
                        counts = {count for _, count in field_counts}
                        most_common_count: int = max(
                            counts,
                            key=lambda x: sum(1 for _, c in field_counts if c == x),
                        )
                        inconsistent_lines: list[tuple[int, int]] = [
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
            return pd.read_excel(file)  # type: ignore[return-value]
    else:
        raise ValueError(
            f"Unsupported file format: {path.suffix}. Only CSV and Excel files are supported."
        )


def read_presets_file(path: Path) -> dict[str, Preset]:
    with open(path, encoding="utf-8") as file:
        # json.load returns Any; no schema validation here, so Any is justified
        presets_data: dict[str, Any] = json.load(file)

        presets: dict[str, Preset] = {}
        for preset_key, preset_config in presets_data.items():
            preset = Preset(
                name=str(preset_config["name"]),
                column_mappings={
                    k: str(v) for k, v in preset_config["column_mappings"].items()
                },
                header_skiprows=int(preset_config["header_skiprows"]),
                footer_skiprows=int(preset_config["footer_skiprows"]),
                del_rows_with=[str(v) for v in preset_config["del_rows_with"]],
                header_mode=str(preset_config.get("header_mode", "fixed")),
            )
            presets[preset_key] = preset

    return presets
