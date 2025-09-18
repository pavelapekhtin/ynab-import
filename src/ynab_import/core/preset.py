"""Preset configuration for transaction data processing."""

from dataclasses import dataclass


@dataclass
class Preset:
    """Configuration preset for processing transaction data."""

    name: str
    column_mappings: dict[str, str]  # YNAB columns -> original columns
    header_skiprows: int
    footer_skiprows: int
    del_rows_with: list[str]
