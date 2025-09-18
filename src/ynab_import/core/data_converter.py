"""Data converter module for transforming transaction data to YNAB format."""

import pandas as pd

from ynab_import.core.preset import Preset


def _rename_columns(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Rename DataFrame columns according to the provided mapping."""
    # Create rename mapping from original columns to YNAB columns
    rename_dict = {}
    for ynab_col, original_col in mapping.items():
        if original_col in df.columns:
            rename_dict[original_col] = ynab_col

    return df.rename(columns=rename_dict)


def _handle_single_amount_column(
    df: pd.DataFrame, mapping: dict[str, str]
) -> pd.DataFrame:
    """Handle case where single column maps to both Inflow and Outflow."""
    # Check if both Inflow and Outflow map to the same original column
    inflow_source = mapping.get("Inflow")
    outflow_source = mapping.get("Outflow")

    # If same column maps to both Inflow and Outflow, split it
    if (
        inflow_source
        and outflow_source
        and inflow_source == outflow_source
        and inflow_source in df.columns
    ):
        amount_col = inflow_source
        df = df.copy()

        # Create Inflow column (positive values)
        df["Inflow"] = df[amount_col].apply(
            lambda x: x if pd.notna(x) and x > 0 else None
        )

        # Create Outflow column (negative values, made positive)
        df["Outflow"] = df[amount_col].apply(
            lambda x: abs(x) if pd.notna(x) and x < 0 else None
        )

        # Remove the original column
        df = df.drop(columns=[amount_col])

    return df


def _format_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """Format the Date column to dd-mm-yyyy format."""
    if "Date" not in df.columns:
        return df

    df = df.copy()

    # Convert to datetime if it's not already
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        # Format as dd-mm-yyyy
        df["Date"] = df["Date"].dt.strftime("%d-%m-%Y")
    except Exception:
        # If conversion fails, leave as-is
        pass

    return df


def _filter_mapped_columns(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Keep only columns that are mapped to YNAB columns."""
    # Get YNAB column names in desired order
    ynab_columns = ["Date", "Payee", "Memo", "Inflow", "Outflow"]

    # Keep only columns that exist and are YNAB columns, in the correct order
    columns_to_keep = [col for col in ynab_columns if col in df.columns]

    return df[columns_to_keep]  # type: ignore


def convert_to_ynab(input_df: pd.DataFrame, preset: Preset) -> pd.DataFrame:
    """Convert input DataFrame to YNAB format according to preset mapping."""
    df = input_df.copy()

    # Step 1: Handle single amount column before renaming
    df = _handle_single_amount_column(df, preset.column_mappings)

    # Step 2: Rename columns according to mapping
    df = _rename_columns(df, preset.column_mappings)

    # Step 3: Format date column to dd-mm-yyyy
    df = _format_date_column(df)

    # Step 4: Keep only mapped YNAB columns
    df = _filter_mapped_columns(df, preset.column_mappings)

    return df
