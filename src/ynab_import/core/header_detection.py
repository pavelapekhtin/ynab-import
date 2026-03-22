from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from pandas import DataFrame

from ynab_import.core.diagnostics import ConversionWarning
from ynab_import.core.preset import Preset

AUTO_DETECT_SEARCH_LIMIT = 15


@dataclass
class HeaderPreparation:
    data: DataFrame
    header_skiprows: int
    footer_skiprows: int
    set_header: bool
    warnings: list[ConversionWarning]


def _normalize_header_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().lower().split())


def _expected_header_names(preset: Preset) -> set[str]:
    return {
        _normalize_header_text(name)
        for name in preset.column_mappings.values()
        if _normalize_header_text(name)
    }


def detect_header_row_from_preset(
    data: DataFrame, preset: Preset, search_limit: int = AUTO_DETECT_SEARCH_LIMIT
) -> int | None:
    expected_headers = _expected_header_names(preset)
    if not expected_headers or data.empty:
        return None

    best_row_index: int | None = None
    best_score = 0

    for index in range(min(len(data), search_limit)):
        row_values = {
            _normalize_header_text(value) for value in data.iloc[index].tolist()
        }
        row_values.discard("")
        score = len(expected_headers & row_values)

        if score > best_score:
            best_score = score
            best_row_index = index

    required_score = 1 if len(expected_headers) == 1 else min(len(expected_headers), 2)
    if best_row_index is None or best_score < required_score:
        return None

    return best_row_index


def suggest_header_row(
    data: DataFrame, search_limit: int = AUTO_DETECT_SEARCH_LIMIT
) -> int:
    if data.empty:
        return 0

    best_row_index = 0
    best_score = -1.0

    for index in range(min(len(data), search_limit)):
        row = data.iloc[index]
        non_empty_values = [
            _normalize_header_text(value)
            for value in row.tolist()
            if _normalize_header_text(value)
        ]

        if not non_empty_values:
            continue

        unique_ratio = len(set(non_empty_values)) / len(non_empty_values)
        alphabetic_cells = sum(
            any(char.isalpha() for char in value) for value in non_empty_values
        )
        score = len(non_empty_values) + unique_ratio + (alphabetic_cells * 0.25)

        if score > best_score:
            best_score = score
            best_row_index = index

    return best_row_index


def prepare_data_for_conversion(data: DataFrame, preset: Preset) -> HeaderPreparation:
    if preset.header_mode != "auto":
        return HeaderPreparation(
            data=data,
            header_skiprows=preset.header_skiprows,
            footer_skiprows=preset.footer_skiprows,
            set_header=preset.header_skiprows > 0,
            warnings=[],
        )

    detected_row = detect_header_row_from_preset(data, preset)
    if detected_row is not None:
        return HeaderPreparation(
            data=data,
            header_skiprows=detected_row,
            footer_skiprows=preset.footer_skiprows,
            set_header=True,
            warnings=[],
        )

    warning = ConversionWarning(
        message=(
            "Header auto-detection could not confidently find the mapped header row. "
            f"Falling back to saved header skip count ({preset.header_skiprows})."
        ),
        stage="header-detect",
    )
    return HeaderPreparation(
        data=data,
        header_skiprows=preset.header_skiprows,
        footer_skiprows=preset.footer_skiprows,
        set_header=preset.header_skiprows > 0,
        warnings=[warning],
    )
