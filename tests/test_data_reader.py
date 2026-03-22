import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import tempfile

import pytest

from ynab_import.file_rw.readers import read_presets_file, read_transaction_file


@pytest.mark.unit
def test_read_transaction_file_unsupported_format() -> None:
    """Test that unsupported file formats raise ValueError."""
    # Arrange
    unsupported_file = Path("test.txt")

    # Act & Assert
    with pytest.raises(ValueError, match="Unsupported file format"):
        read_transaction_file(unsupported_file)


@pytest.mark.unit
def test_read_transaction_file_nonexistent_file() -> None:
    """Test that nonexistent files raise appropriate exception."""
    # Arrange
    nonexistent_file = Path("nonexistent.csv")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        read_transaction_file(nonexistent_file)


@pytest.mark.unit
def test_read_presets_file_nonexistent() -> None:
    """Test that nonexistent preset files raise FileNotFoundError."""
    # Arrange
    nonexistent_file = Path("nonexistent_presets.json")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        read_presets_file(nonexistent_file)


@pytest.mark.unit
def test_read_presets_file_invalid_json() -> None:
    """Test that invalid JSON raises JSONDecodeError."""
    # Arrange
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{ invalid json content")
        invalid_json_path = Path(f.name)

    try:
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            read_presets_file(invalid_json_path)
    finally:
        # Cleanup
        invalid_json_path.unlink()


@pytest.mark.unit
def test_read_presets_file_defaults_header_mode_for_legacy_json() -> None:
    """Test legacy presets without header_mode default to fixed."""
    preset_json = {
        "legacy": {
            "name": "Legacy Preset",
            "column_mappings": {"Date": "Date", "Outflow": "Amount"},
            "header_skiprows": 1,
            "footer_skiprows": 0,
            "del_rows_with": [],
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as file:
        json.dump(preset_json, file)
        preset_path = Path(file.name)

    try:
        presets = read_presets_file(preset_path)
        assert presets["legacy"].header_mode == "fixed"
    finally:
        preset_path.unlink()
