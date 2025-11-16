"""Complete CLI interface for YNAB import tool using questionary for interactive prompts."""

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd
import questionary
from questionary import Choice
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ynab_import import get_version
from ynab_import.cli.ascii_art import ynab_banner
from ynab_import.core.clean_input import (
    delete_rows_containing_text,
    remove_header_footer,
)
from ynab_import.core.config import (
    delete_preset,
    ensure_config_exists,
    load_presets,
    save_preset,
    update_config_value,
)
from ynab_import.core.pipeline import convert_file_with_preset, preview_conversion
from ynab_import.core.preset import Preset
from ynab_import.file_rw.readers import read_transaction_file

# Initialize Rich console with Catppuccin-inspired colors
console = Console()

# Catppuccin-inspired color scheme
COLORS = {
    "primary": "#cba6f7",  # Purple
    "secondary": "#89b4fa",  # Blue
    "success": "#a6e3a1",  # Green
    "warning": "#f9e2af",  # Yellow
    "error": "#f38ba8",  # Red
    "text": "#cdd6f4",  # Text
    "subtext": "#a6adc8",  # Subtext
    "surface": "#313244",  # Surface
}

# Questionary theme configuration
QUESTIONARY_THEME = questionary.Style(
    [
        ("qmark", "fg:#000000"),
        ("question", "fg:#cba6f7 bold"),
        ("answer", "fg:#a6e3a1 bold"),
        ("pointer", "fg:#000000 bold"),
        ("highlighted", "fg:#313244 bg:#cba6f7"),
        ("selected", "fg:#a6e3a1"),
        ("separator", "fg:#6c7086"),
        ("instruction", ""),
        ("text", "fg:#cdd6f4"),
        ("disabled", "fg:#6c7086 italic"),
    ]
)


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def get_terminal_width() -> int:
    """Get the terminal width for centering content."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def center_text(text: str, width: int | None = None) -> str:
    """Center text within the terminal width."""
    if width is None:
        width = get_terminal_width()
    lines = text.strip().split("\n")
    centered_lines = []
    for line in lines:
        padding = (width - len(line)) // 2
        centered_lines.append(" " * padding + line)
    return "\n".join(centered_lines)


def display_header() -> None:
    """Display the centered YNAB banner and status information."""
    clear_screen()

    # Display centered banner
    banner_text = Text(ynab_banner, style=COLORS["primary"])
    console.print(Align.left(banner_text))

    # Display version under the banner
    version_text = Text(f"v{get_version()}", style=COLORS["subtext"])
    console.print(Align.left(version_text))
    console.print()

    # Load config for status display
    config = ensure_config_exists()

    # Status panel
    preset_status: str
    path_status: str

    # Active preset
    if config.active_preset:
        presets = load_presets()
        preset_name = presets.get(config.active_preset, None)
        if preset_name:
            preset_status = f"[{COLORS['success']}]{preset_name.name}[/]"
        else:
            preset_status = f"[{COLORS['error']}]Invalid preset[/]"
    else:
        preset_status = f"[{COLORS['error']}]Not selected[/]"

    # Export folder
    if config.export_path:
        path_status = f"[{COLORS['secondary']}]{config.export_path}[/]"
    else:
        path_status = f"[{COLORS['error']}]Not set[/]"

    preset_status_panel = Panel(
        Align.center(preset_status),
        title="[bold]Active Preset",
        border_style=COLORS["warning"],
        padding=(1, 1),
    )

    export_path_status_panel = Panel(
        (path_status),
        title="[bold]Export Path",
        border_style=COLORS["secondary"],
        padding=(1, 1),
    )

    columns = Columns([preset_status_panel, export_path_status_panel], equal=True)

    console.print(Align.left(columns))
    console.print()


def ask_with_menu(
    choices: list[str | questionary.Separator], message: str = "Select an option:"
) -> str | None:
    """Display a menu and get user selection using questionary."""
    try:
        return questionary.select(
            message,
            choices=choices,
            style=QUESTIONARY_THEME,
            instruction=" ",
        ).ask()
    except KeyboardInterrupt:
        return None


def path_input(
    message: str = "Enter path: ", must_exist: bool = False, is_directory: bool = False
) -> Path | None:
    """Get path input from user with validation and ~ expansion."""
    # Show completion tips

    while True:
        try:
            user_input = questionary.path(
                message,
                only_directories=is_directory,
                style=QUESTIONARY_THEME,
                # instruction=" ",
            ).ask()

            if not user_input:
                return None

            if not user_input.strip():
                console.print(f"[{COLORS['warning']}]Please enter a path.[/]")
                continue

            # Expand ~ to home directory and resolve the path
            try:
                path = Path(user_input).expanduser().resolve()
            except (OSError, ValueError) as e:
                console.print(f"[{COLORS['error']}]Invalid path format:[/] {e}")
                continue

            if must_exist and not path.exists():
                console.print(f"[{COLORS['error']}]Path does not exist:[/] {path}")
                continue

            if is_directory and path.exists() and not path.is_dir():
                console.print(f"[{COLORS['error']}]Path is not a directory:[/] {path}")
                continue

            return path

        except KeyboardInterrupt:
            console.print(f"\n[{COLORS['warning']}]Cancelled.[/]")
            return None
        except Exception as e:
            console.print(f"[{COLORS['error']}]Unexpected error:[/] {e}")
            continue


def text_input(message: str, default: str = "") -> str | None:
    """Get text input from user."""
    try:
        return questionary.text(message, default=default, style=QUESTIONARY_THEME).ask()
    except KeyboardInterrupt:
        return None


def confirm_input(message: str, default: bool = True) -> bool | None:
    """Get confirmation from user."""
    try:
        return questionary.confirm(
            message, default=default, style=QUESTIONARY_THEME
        ).ask()
    except KeyboardInterrupt:
        return None


def integer_input(message: str, default: int = 0) -> int | None:
    """Get integer input from user with validation."""
    while True:
        try:
            result = text_input(f"{message} (default: {default})")
            if result is None:
                return None
            if not result.strip():
                return default
            return int(result)
        except ValueError:
            console.print(f"[{COLORS['error']}]Please enter a valid number.[/]")


def display_dataframe_preview(df: pd.DataFrame, title: str, max_rows: int = 10) -> None:
    """Display a DataFrame preview using Rich table."""
    table = Table(title=title, style=COLORS["surface"])

    # Add columns with header styling
    for col in df.columns:
        table.add_column(
            str(col), style=COLORS["primary"], header_style=COLORS["secondary"]
        )

    # Add rows with alternating styles (limit to max_rows)
    for i, (_, row) in enumerate(df.head(max_rows).iterrows()):
        row_style = COLORS["text"] if i % 2 == 0 else COLORS["subtext"]
        styled_values = [f"[{row_style}]{val!s}[/]" for val in row]
        table.add_row(*styled_values)

    if len(df) > max_rows:
        table.add_row(
            *[
                f"[{COLORS['warning']}]... ({len(df) - max_rows} more rows)[/]"
                for _ in df.columns
            ]
        )

    console.print(table)


def convert_file_menu() -> None:
    """Handle file conversion."""
    display_header()

    config = ensure_config_exists()

    if not config.active_preset:
        console.print(f"[{COLORS['error']}]No active preset selected![/]")
        console.print("Please select a preset first from the main menu.")
        input("\nPress Enter to continue...")
        return

    # Load the preset
    presets = load_presets()
    if config.active_preset not in presets:
        console.print(
            f"[{COLORS['error']}]Active preset '{config.active_preset}' not found![/]"
        )
        input("\nPress Enter to continue...")
        return

    preset = presets[config.active_preset]

    console.print(f"[{COLORS['secondary']}]   Using preset:[/] {preset.name}")

    # Get input file
    console.print("\n[bold green]   Select input file to convert: [/]")
    input_file = path_input(" Path to transaction file: ", must_exist=True)

    if not input_file:
        return

    # Validate file format
    supported_formats = [".csv", ".xlsx", ".xls"]
    if input_file.suffix.lower() not in supported_formats:
        console.print(
            f"[{COLORS['error']}]Unsupported file format:[/] {input_file.suffix}"
        )
        console.print(
            f"[{COLORS['subtext']}]Supported formats:[/] {', '.join(supported_formats)}"
        )
        input("\nPress Enter to continue...")
        return

    # Use preset name as output filename (sanitized for filesystem)
    output_name = re.sub(r"[^\w\-_\. ]", "_", preset.name)

    # Convert the file
    try:
        output_dir = Path(config.export_path)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        console.print(f"\n[{COLORS['secondary']}]Converting file...[/]")

        output_path = convert_file_with_preset(
            input_file, preset, output_dir, output_name
        )

        console.print(f"\n[{COLORS['success']}]✓ Conversion completed successfully![/]")
        console.print(f"[{COLORS['text']}]Saved to:[/] {output_path}")
        console.print(
            f"[{COLORS['subtext']}]File size:[/] {output_path.stat().st_size} bytes"
        )

    except Exception as e:
        console.print(f"\n[{COLORS['error']}]✗ Conversion failed:[/] {e!s}")

        # Check if this is a CSV parsing error and provide helpful info
        error_str = str(e).lower()
        if any(
            keyword in error_str
            for keyword in ["tokenizing", "expected", "fields", "saw", "csv"]
        ):
            console.print(
                f"\n[{COLORS['warning']}]This appears to be a CSV parsing error.[/]"
            )
            console.print(
                f"[{COLORS['subtext']}]Common causes: inconsistent field counts, unescaped quotes, or delimiter issues.[/]"
            )

    input("\nPress Enter to continue...")


def select_preset_menu() -> None:
    """Handle preset selection."""
    display_header()

    presets = load_presets()

    if not presets:
        console.print(f"[{COLORS['warning']}]No presets available![/]")
        console.print("Create a preset first from the main menu.")
        input("\nPress Enter to continue...")
        return

    console.print(f"[{COLORS['warning']}]   Available Presets:[/]\n")

    preset_choices = []
    for key, preset in presets.items():
        preset_choices.append(Choice(preset.name, value=key))

    preset_choices.append(Choice("← Back to Main Menu", value=None))

    selection = ask_with_menu([choice.title for choice in preset_choices], " ")

    if selection and selection != "← Back to Main Menu":
        # Find the corresponding key
        preset_key = None
        for choice in preset_choices:
            if choice.title == selection:
                preset_key = choice.value
                break

        if preset_key:
            # Update config
            update_config_value("active_preset", preset_key)

            console.print(
                f"\n[{COLORS['success']}]✓ Preset '{presets[preset_key].name}' selected![/]"
            )
            input("\nPress Enter to continue...")


def create_preset_menu() -> None:
    """Handle interactive preset creation."""
    display_header()

    console.print(f"[{COLORS['warning']} bold] Create New Preset[/]\n")

    # Get sample file
    console.print("  Select a sample transaction file to analyze:")
    sample_file = path_input("Path to sample file: ", must_exist=True)

    if not sample_file:
        return

    try:
        # Read the sample file
        raw_data = read_transaction_file(sample_file)

        clear_screen()
        console.print("[bold]File Preview[/]\n")

        # Show first 10 rows
        display_dataframe_preview(
            raw_data.head(10), "Original File - First 10 rows", max_rows=10
        )
        console.print()

        # Show last 3 rows
        display_dataframe_preview(
            raw_data.tail(3), "Original File - Last 3 rows", max_rows=3
        )

    except Exception as e:
        console.print(f"[{COLORS['error']}]Error reading file:[/] {e!s}")
        input("\nPress Enter to continue...")
        return

    # Start preset creation
    preset_name = text_input("\nEnter preset name:")
    if not preset_name or not preset_name.strip():
        console.print(f"[{COLORS['error']}]Preset name cannot be empty![/]")
        input("Press Enter to continue...")
        return

    # Initialize preset data
    column_mappings = {}
    current_data = raw_data.copy()

    # Ask for header skip rows
    header_skiprows = integer_input("Number of header rows to skip", default=0)
    if header_skiprows is None:
        return

    # Ask for footer skip rows
    footer_skiprows = integer_input("Number of footer rows to skip", default=0)
    if footer_skiprows is None:
        return

    # Apply header/footer removal and show preview
    if header_skiprows > 0 or footer_skiprows > 0:
        current_data = remove_header_footer(
            current_data, header_skiprows, footer_skiprows
        )

        clear_screen()
        console.print("[bold]Preview After Removing Headers/Footers[/]\n")
        display_dataframe_preview(
            current_data.head(10), "After header/footer removal", max_rows=10
        )
        console.print()

    # Ask about row deletion
    console.print(f"\n[{COLORS['secondary']}]Row Deletion Setup[/]")
    del_rows_with = []

    should_delete_rows = confirm_input(
        "Do you want to delete rows containing specific text?", default=False
    )
    if should_delete_rows is None:
        return

    if should_delete_rows:
        console.print("\nEnter text patterns to delete (empty to finish):")
        while True:
            text_pattern = text_input("Text pattern (or press Enter to finish):")
            if text_pattern is None:
                return
            if not text_pattern.strip():
                break
            del_rows_with.append(text_pattern)

        # Apply row deletion and show preview
        if del_rows_with:
            current_data = delete_rows_containing_text(current_data, del_rows_with)

            clear_screen()
            console.print("[bold]Preview After Row Deletion[/]\n")
            display_dataframe_preview(
                current_data.head(10), "After deleting specified rows", max_rows=10
            )
            console.print()

    # Set header from first row if needed
    should_set_header = confirm_input("Use first row as column headers?", default=True)

    if should_set_header is None:
        return

    if should_set_header:
        if len(current_data) > 0:
            new_columns = current_data.iloc[0].astype(str).tolist()
            current_data = current_data.iloc[1:].reset_index(drop=True)
            current_data.columns = new_columns

            clear_screen()
            console.print("[bold]Preview After Setting Column Headers[/]\n")
            display_dataframe_preview(
                current_data.head(10),
                "After setting headers from first row",
                max_rows=10,
            )
            console.print()

    # Show final cleaned preview before column mapping
    clear_screen()
    console.print("[bold]Final Cleaned Data Preview[/]\n")
    display_dataframe_preview(
        current_data.head(5), "Ready for column mapping", max_rows=5
    )

    # Column mapping
    console.print(f"\n[{COLORS['secondary']}]Column Mapping[/]\n")

    ynab_columns = ["Date", "Payee", "Memo", "Inflow", "Outflow"]
    mapping_results = []  # Store results for display

    # Build choices for all columns
    choices = []
    for col in current_data.columns:
        if len(current_data) > 0:
            try:
                # Get sample value with safe handling
                raw_val = current_data[col].iloc[0]
                if pd.isna(raw_val) or raw_val is None:
                    sample_val = "N/A"
                else:
                    sample_val = str(raw_val)

                    # Sanitize for display
                    sample_val = "".join(
                        char
                        for char in sample_val
                        if ord(char) >= 32 and ord(char) <= 126
                    )

                    sample_val = (
                        sample_val.replace("\n", " ")
                        .replace("\r", " ")
                        .replace("\t", " ")
                    )

                    sample_val = " ".join(sample_val.split())

                    if not sample_val.strip():
                        sample_val = "N/A"

                    if len(sample_val) > 20:
                        sample_val = sample_val[:20] + "..."

            except (IndexError, ValueError, TypeError, UnicodeError):
                sample_val = "N/A"
        else:
            sample_val = "N/A"

        col_clean = str(col).strip()
        display_text = f"{col_clean} -> {sample_val}"
        choices.append(Choice(display_text, value=col))

    choices.append(Choice("Skip this column", value=None))

    # Create a mapping dictionary for easier lookup
    choice_map = {}
    choice_titles = []

    for choice in choices:
        choice_titles.append(choice.title)
        choice_map[choice.title] = choice.value

    for _i, ynab_col in enumerate(ynab_columns):
        # Clear screen and show data preview + accumulated results
        clear_screen()
        display_dataframe_preview(
            current_data.head(5), "Ready for column mapping", max_rows=5
        )

        console.print(f"\n[{COLORS['secondary']}]Column Mapping[/]\n")

        # Display previous results
        for result_line in mapping_results:
            console.print(result_line)

        if mapping_results:  # Add spacing if there are previous results
            console.print()

        result = questionary.select(
            f"Select source column for {ynab_col}:",
            choices=choice_titles,
            style=QUESTIONARY_THEME,
        ).ask()

        if result is None:  # User cancelled
            return

        if result == "Skip this column":
            mapping_results.append(
                f"[{COLORS['warning']}]▲ Skipped {ynab_col} column[/]"
            )
        else:
            # Get the actual source column from the choice map
            source_col = choice_map.get(result)
            if source_col is not None:
                column_mappings[ynab_col] = source_col
                mapping_results.append(
                    f"[{COLORS['success']}]✓ Mapped {ynab_col} to {source_col}[/]"
                )
            else:
                mapping_results.append(
                    f"[{COLORS['error']}]✗ Error mapping {ynab_col}[/]"
                )

    # Show final mapping results
    clear_screen()
    display_dataframe_preview(
        current_data.head(5), "Ready for column mapping", max_rows=5
    )

    console.print(f"\n[{COLORS['secondary']}]Column Mapping Complete[/]\n")
    for result_line in mapping_results:
        console.print(result_line)
    console.print()

    # Create preset
    preset = Preset(
        name=preset_name,
        column_mappings=column_mappings,
        header_skiprows=header_skiprows,
        footer_skiprows=footer_skiprows,
        del_rows_with=del_rows_with,
    )

    # Show final preview
    try:
        preview_data = preview_conversion(
            raw_data, preset, set_header=should_set_header
        )

        clear_screen()
        console.print("[bold]Final Preview[/]\n")
        display_dataframe_preview(
            preview_data.head(5), "YNAB Format Preview", max_rows=5
        )

        # Ask to save
        console.print(f"\n[{COLORS['secondary']}]Save this preset?[/]")
        should_save = confirm_input("Save preset?", default=True)
        if should_save is None:
            return

        if should_save:
            preset_key = preset_name.lower().replace(" ", "_")
            save_preset(preset_key, preset)

            console.print(f"\n[{COLORS['success']}]✓ Preset '{preset_name}' saved![/]")

            # Ask to set as active
            should_activate = confirm_input("Set as active preset?", default=True)
            if should_activate is None:
                return

            if should_activate:
                update_config_value("active_preset", preset_key)
                console.print(f"[{COLORS['success']}]✓ Preset set as active![/]")

    except Exception as e:
        console.print(f"\n[{COLORS['error']}]Error generating preview:[/] {e!s}")

    input("\nPress Enter to continue...")


def delete_preset_menu() -> None:
    """Handle preset deletion."""
    display_header()

    presets = load_presets()

    if not presets:
        console.print(f"[{COLORS['warning']}]No presets available to delete![/]")
        input("\nPress Enter to continue...")
        return

    console.print("[bold red]   Delete Preset[/]\n")

    preset_choices = []
    for key, preset in presets.items():
        preset_choices.append(Choice(preset.name, value=key))

    preset_choices.append(Choice("← Back to Main Menu", value=None))

    selection = ask_with_menu(
        [choice.title for choice in preset_choices],
        "",
    )

    if selection and selection != "← Back to Main Menu":
        # Find the corresponding key
        preset_key = None
        for choice in preset_choices:
            if choice.title == selection:
                preset_key = choice.value
                break

        if preset_key:
            preset_name = presets[preset_key].name

            # Confirm deletion
            console.print(
                f"\n[{COLORS['warning']}]Are you sure you want to delete '{preset_name}'?[/]"
            )
            console.print("[red]This action cannot be undone![/]")

            should_delete = confirm_input("Delete preset?", default=False)
            if should_delete is None:
                return

            if should_delete:
                if delete_preset(preset_key):
                    console.print(
                        f"\n[{COLORS['success']}]✓ Preset '{preset_name}' deleted![/]"
                    )

                    # Clear active preset if it was the deleted one
                    config = ensure_config_exists()
                    if config.active_preset == preset_key:
                        update_config_value("active_preset", None)
                        console.print(f"[{COLORS['warning']}]Active preset cleared.[/]")
                else:
                    console.print(f"\n[{COLORS['error']}]Failed to delete preset![/]")

            input("\nPress Enter to continue...")


def set_export_path_menu() -> None:
    """Handle export path configuration."""
    display_header()

    config = ensure_config_exists()

    console.print("[bold]   Set Export Path[/]\n")

    if config.export_path:
        console.print(
            f"   Current export path: [{COLORS['secondary']}]{config.export_path}[/]\n"
        )
    else:
        console.print(f"Current export path: [{COLORS['error']}]Not set[/]\n")

    # Get new export path
    console.print("   Select new export directory:")
    new_path = path_input(
        " Export directory path: ", must_exist=False, is_directory=True
    )

    if not new_path:
        return

    # Create directory if it doesn't exist
    try:
        new_path.mkdir(parents=True, exist_ok=True)

        # Update config
        update_config_value("export_path", str(new_path))

        console.print(f"\n[{COLORS['success']}]✓ Export path updated to:[/] {new_path}")

    except Exception as e:
        console.print(f"\n[{COLORS['error']}]Failed to create/set export path:[/] {e}")

    input("\nPress Enter to continue...")


def main_menu() -> None:
    """Display and handle the main menu."""
    # Parse command line arguments first
    parser = argparse.ArgumentParser(
        prog="ynab-converter",
        description="Convert bank export files to YNAB-compatible CSV format",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {get_version()}"
    )

    # Only parse args if they exist (skip in interactive mode)
    if len(sys.argv) > 1:
        parser.parse_args()
        return  # Exit after handling version

    menu_items = [
        "Convert File",
        "Select Preset",
        questionary.Separator("  "),
        "Create Preset",
        "Delete Preset",
        "Set Export Path",
        questionary.Separator("  "),
        "Exit",
    ]

    while True:
        display_header()

        console.print(f"[{COLORS['warning']} bold]   MAIN MENU\n")

        selection = ask_with_menu(menu_items, " ")

        if selection == "Convert File":
            convert_file_menu()
        elif selection == "Select Preset":
            select_preset_menu()
        elif selection == "Create Preset":
            create_preset_menu()
        elif selection == "Delete Preset":
            delete_preset_menu()
        elif selection == "Set Export Path":
            set_export_path_menu()
        elif selection == "Exit":
            clear_screen()
            console.print(f"[{COLORS['success']}]Thanks for using YNAB Import Tool![/]")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        clear_screen()
        console.print(f"\n[{COLORS['warning']}]Application interrupted. Goodbye![/]")
        sys.exit(0)
