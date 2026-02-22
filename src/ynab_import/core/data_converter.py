from __future__ import annotations

import warnings

import pandas as pd
from pandas import DataFrame

from ynab_import.core.preset import Preset


def _rename_columns(df: DataFrame, mapping: dict[str, str]) -> DataFrame:
    rename_dict: dict[str, str] = {}
    for ynab_col, original_col in mapping.items():
        if original_col in df.columns:
            rename_dict[original_col] = ynab_col
    return df.rename(columns=rename_dict)


def _handle_single_amount_column(df: DataFrame, mapping: dict[str, str]) -> DataFrame:
    inflow_source = mapping.get("Inflow")
    outflow_source = mapping.get("Outflow")

    if (
        inflow_source
        and outflow_source
        and inflow_source == outflow_source
        and inflow_source in df.columns
    ):
        amount_col = inflow_source
        df = df.copy()

        df["Inflow"] = df[amount_col].apply(  # type: ignore[index]
            lambda x: x if pd.notna(x) and float(x) > 0 else None  # type: ignore[arg-type]
        )
        df["Outflow"] = df[amount_col].apply(  # type: ignore[index]
            lambda x: abs(float(x)) if pd.notna(x) and float(x) < 0 else None  # type: ignore[arg-type]
        )
        df = df.drop(columns=[amount_col])

    return df


def _format_date_column(df: DataFrame) -> DataFrame:
    if "Date" not in df.columns:
        return df

    df = df.copy()

    try:
        common_formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]

        parsed_series: pd.Series | None = None
        for fmt in common_formats:
            try:
                parsed_series = pd.to_datetime(df["Date"], format=fmt, errors="raise")  # type: ignore[assignment]
                break
            except (ValueError, TypeError):
                continue

        if parsed_series is None:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Could not infer format")
                parsed_series = pd.to_datetime(df["Date"], errors="coerce")  # type: ignore[assignment]

        df["Date"] = parsed_series
        df["Date"] = df["Date"].dt.strftime("%d-%m-%Y")  # type: ignore[union-attr]
    except Exception:
        pass

    return df


def _filter_mapped_columns(df: DataFrame, mapping: dict[str, str]) -> DataFrame:
    ynab_columns = ["Date", "Payee", "Memo", "Inflow", "Outflow"]
    columns_to_keep = [col for col in ynab_columns if col in df.columns]
    return df[columns_to_keep]  # type: ignore[return-value]


def convert_to_ynab(input_df: DataFrame, preset: Preset) -> DataFrame:
    df = input_df.copy()
    df = _handle_single_amount_column(df, preset.column_mappings)
    df = _rename_columns(df, preset.column_mappings)
    df = _format_date_column(df)
    df = _filter_mapped_columns(df, preset.column_mappings)
    return df
