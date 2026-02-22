from __future__ import annotations

import pandas as pd
from pandas import DataFrame, Series

from ynab_import.core.preset import Preset


def remove_header_footer(
    data: DataFrame, header_rows: int = 0, footer_rows: int = 0
) -> DataFrame:
    result: DataFrame = data.iloc[header_rows:] if header_rows > 0 else data
    if footer_rows > 0:
        result = result.iloc[:-footer_rows]
    return result.reset_index(drop=True)  # type: ignore[return-value]


def delete_rows_containing_text(
    data: DataFrame, text_list: list[str] | None = None
) -> DataFrame:
    if not text_list or data.empty:
        return data.copy()

    data_str: DataFrame = data.astype(str)
    rows_to_keep: Series = Series([True] * len(data), index=data.index)  # type: ignore

    for text in text_list:
        if text:
            text_str = str(text)
            contains_text: Series[bool] = data_str.apply(  # type: ignore[assignment]
                lambda row, t=text_str: row.str.contains(t, na=False).any(),  # type: ignore[union-attr]
                axis=1,
            )
            rows_to_keep &= ~contains_text

    return data[rows_to_keep].reset_index(drop=True)  # type: ignore[return-value]


def set_first_row_as_header(data: DataFrame) -> DataFrame:
    if len(data) == 0:
        return data

    new_columns: list[str] = data.iloc[0].astype(str).tolist()
    result: DataFrame = data.iloc[1:].reset_index(drop=True)  # type: ignore[assignment]
    result.columns = pd.Index(new_columns)
    return result


def clean_data_pipeline(
    data: DataFrame,
    header_rows: int = 0,
    footer_rows: int = 0,
    del_rows_with: list[str] | None = None,
    set_header: bool = False,
) -> DataFrame:
    result = data.copy()
    result = remove_header_footer(result, header_rows, footer_rows)
    result = delete_rows_containing_text(result, del_rows_with)
    if set_header:
        result = set_first_row_as_header(result)
    return result


def clean_data_with_preset(
    data: DataFrame, preset: Preset, set_header: bool = False
) -> DataFrame:
    return clean_data_pipeline(
        data,
        header_rows=preset.header_skiprows,
        footer_rows=preset.footer_skiprows,
        del_rows_with=preset.del_rows_with,
        set_header=set_header,
    )
