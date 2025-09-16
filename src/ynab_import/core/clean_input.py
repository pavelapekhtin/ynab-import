"""Data cleaning utilities for transaction files."""

import pandas as pd

from ynab_import.core.preset import Preset


def remove_header_footer(
    data: pd.DataFrame, header_rows: int = 0, footer_rows: int = 0
) -> pd.DataFrame:
    """Remove specified number of rows from top and bottom of DataFrame."""
    # Remove rows from the top
    if header_rows > 0:
        data = data.iloc[header_rows:]

    # Remove rows from the bottom
    if footer_rows > 0:
        data = data.iloc[:-footer_rows]

    # Reset index after removing rows
    return data.reset_index(drop=True)


def delete_rows_containing_text(
    data: pd.DataFrame, text_list: list[str] | None = None
) -> pd.DataFrame:
    """Remove rows from DataFrame that contain any of the specified text strings."""
    if not text_list or data.empty:
        return data.copy()

    # Convert all DataFrame values to strings for text matching
    data_str = data.astype(str)

    # Create boolean mask for rows to keep
    rows_to_keep = pd.Series([True] * len(data), index=data.index)

    # Check each text string
    for text in text_list:
        if text:  # Skip empty strings
            # Check if any cell in each row contains the text
            text_str = str(text)  # Capture the text value in local scope
            contains_text = data_str.apply(
                lambda row, t=text_str: row.str.contains(t, na=False).any(), axis=1
            )
            rows_to_keep &= ~contains_text

    # Filter the DataFrame and reset index
    return data[rows_to_keep].reset_index(drop=True)  # type: ignore


def set_first_row_as_header(data: pd.DataFrame) -> pd.DataFrame:
    """Set the first row of the DataFrame as column headers."""
    if len(data) == 0:
        return data

    # Get the first row values as new column names
    new_columns = data.iloc[0].astype(str).tolist()

    # Remove the first row and reset index
    data = data.iloc[1:].reset_index(drop=True)

    # Set new column names
    data.columns = new_columns

    return data


def clean_data_pipeline(
    data: pd.DataFrame,
    header_rows: int = 0,
    footer_rows: int = 0,
    del_rows_with: list[str] | None = None,
    set_header: bool = False,
) -> pd.DataFrame:
    """Apply a complete cleaning pipeline to transaction data."""
    result = data.copy()

    # Step 1: Remove header/footer rows
    result = remove_header_footer(result, header_rows, footer_rows)

    # Step 2: Delete rows containing specified text
    result = delete_rows_containing_text(result, del_rows_with)

    # Step 3: Set first row as headers if requested
    if set_header:
        result = set_first_row_as_header(result)

    return result


def clean_data_with_preset(
    data: pd.DataFrame, preset: Preset, set_header: bool = False
) -> pd.DataFrame:
    """Apply cleaning pipeline using a Preset object configuration."""
    return clean_data_pipeline(
        data,
        header_rows=preset.header_skiprows,
        footer_rows=preset.footer_skiprows,
        del_rows_with=preset.del_rows_with,
        set_header=set_header,
    )
