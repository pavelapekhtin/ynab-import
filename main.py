"""Main entry point for the YNAB Import CLI application."""

from ynab_import.cli.menus import main_menu


def main() -> None:
    """Run the YNAB Import CLI application."""
    main_menu()


if __name__ == "__main__":
    main()
