"""YNAB Import Tool - Convert bank export files to YNAB-compatible CSV format."""

__version__ = "0.2.0"
__author__ = "Pavel Apekhtin"
__email__ = "pavelapekdev@gmail.com"
__description__ = (
    "A powerful CLI tool for converting bank export files to YNAB-compatible CSV format"
)

# Expose main functionality
from ynab_import.cli.menus import main_menu

__all__ = ["__version__", "main_menu"]
