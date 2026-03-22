from __future__ import annotations

import re
import warnings
from decimal import Decimal, InvalidOperation

import pandas as pd
from pandas import DataFrame

from ynab_import.core.preset import Preset


class AmountParseError(ValueError):
    def __init__(self, column: str, row_index: int, raw_value: object) -> None:
        self.column = column
        self.row_index = row_index
        self.raw_value = raw_value
        super().__init__(
            f"Unable to parse amount value {raw_value!r} in column '{column}' at row {row_index}."
        )


def _normalize_amount_value(value: object) -> float | None:
    if pd.isna(value):
        return None

    if isinstance(value, int | float):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]

    text = text.replace("\u00a0", " ")
    text = text.replace(" ", "")
    text = re.sub(r"[^\d,.\-+]", "", text)

    if not text:
        return None

    if text.count("-") > 1 or ("-" in text and not text.startswith("-")):
        raise InvalidOperation("invalid negative amount format")

    if text.startswith("-"):
        negative = True
        text = text[1:]
    elif text.startswith("+"):
        text = text[1:]

    if not text:
        raise InvalidOperation("amount contained only sign")

    comma_pos = text.rfind(",")
    dot_pos = text.rfind(".")

    if comma_pos != -1 and dot_pos != -1:
        decimal_separator = "," if comma_pos > dot_pos else "."
    elif comma_pos != -1:
        decimal_separator = "," if len(text) - comma_pos - 1 != 3 else None
    elif dot_pos != -1:
        decimal_separator = "." if len(text) - dot_pos - 1 != 3 else None
    else:
        decimal_separator = None

    if decimal_separator == ",":
        normalized = text.replace(".", "").replace(",", ".")
    elif decimal_separator == ".":
        normalized = text.replace(",", "")
    else:
        normalized = text.replace(",", "").replace(".", "")

    amount = float(Decimal(normalized))
    return -amount if negative else amount


def _normalize_amount_series(df: DataFrame, column: str) -> pd.Series:
    normalized_values: list[float | None] = []
    for row_index, value in enumerate(df[column].tolist()):
        try:
            normalized_values.append(_normalize_amount_value(value))
        except (InvalidOperation, ValueError) as error:
            if pd.isna(value) or not str(value).strip():
                normalized_values.append(None)
                continue
            raise AmountParseError(column, row_index, value) from error

    return pd.Series(normalized_values, index=df.index, dtype="float64")


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
        parsed_amounts = _normalize_amount_series(df, amount_col)

        df["Inflow"] = parsed_amounts.apply(
            lambda x: x if pd.notna(x) and float(x) > 0 else None
        )
        df["Outflow"] = parsed_amounts.apply(
            lambda x: abs(float(x)) if pd.notna(x) and float(x) < 0 else None
        )
        df = df.drop(columns=[amount_col])

    return df


def _normalize_mapped_amount_columns(
    df: DataFrame, mapping: dict[str, str]
) -> DataFrame:
    df = df.copy()
    for ynab_column in ("Inflow", "Outflow"):
        source_column = mapping.get(ynab_column)
        if source_column and source_column in df.columns:
            df[source_column] = _normalize_amount_series(df, source_column)
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
    df = _normalize_mapped_amount_columns(df, preset.column_mappings)
    df = _handle_single_amount_column(df, preset.column_mappings)
    df = _rename_columns(df, preset.column_mappings)
    df = _format_date_column(df)
    df = _filter_mapped_columns(df, preset.column_mappings)
    return df
