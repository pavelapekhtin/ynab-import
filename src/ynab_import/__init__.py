"""YNAB Import Tool - Convert bank export files to YNAB-compatible CSV format."""

try:
    from importlib.metadata import version

    __version__ = version("ynab-converter")
except Exception:
    # Fallback for older Python versions or missing package
    try:
        from importlib_metadata import version

        __version__ = version("ynab-converter")
    except Exception:
        # Fallback version if package not installed
        __version__ = "0.5.0"

__author__ = "Pavel Apekhtin"
__email__ = "pavelapekdev@gmail.com"
__description__ = (
    "A powerful CLI tool for converting bank export files to YNAB-compatible CSV format"
)


def get_version() -> str:
    """Get the current version of the package."""
    return __version__


def main_menu():
    """Lazy import of main_menu to avoid circular dependencies."""
    from ynab_import.cli.menus import main_menu as _main_menu

    return _main_menu()


__all__ = ["__version__", "get_version", "main_menu"]
