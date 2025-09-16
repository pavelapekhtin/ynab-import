#!/usr/bin/env python3
"""Main entry point for YNAB Import Tool CLI."""

import sys
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ynab_import.cli.menus import main_menu

if __name__ == "__main__":
    main_menu()
