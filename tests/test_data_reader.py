import json
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ynab_import.core.preset import Preset
from ynab_import.file_rw.readers import read_presets_file, read_transaction_file


@pytest.mark.unit
@pytest.mark.parametrize("test_file", ["bulder.csv", "Erurocard.xlsx"])
def test_read_transaction_file(test_file) -> None:  # noqa: ANN001
    """Test reading transaction files (CSV and Excel) into pandas DataFrame."""
    # Arrange
    sample_file_path = Path(__file__).parent / "sample_files" / test_file

    # Act
    result_df = read_transaction_file(sample_file_path)

    # Assert
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty

    # Basic structure validation - just ensure we got some columns and rows
    assert len(result_df.columns) > 0
    assert len(result_df) > 0


@pytest.mark.unit
@pytest.mark.csv
@pytest.mark.parametrize("test_file", ["bulder.csv"])
def test_read_csv_specific_structure(test_file) -> None:  # noqa: ANN001
    """Test CSV file specific structure validation."""
    # Arrange
    sample_file_path = Path(__file__).parent / "sample_files" / test_file

    # Act
    result_df = read_transaction_file(sample_file_path)

    # Assert CSV specific structure
    expected_columns = [
        "Dato",
        "Beløp",
        "Originalt Beløp",
        "Original Valuta",
        "Til konto",
        "Til kontonummer",
        "Fra konto",
        "Fra kontonummer",
        "Type",
        "Tekst",
        "KID",
        "Hovedkategori",
        "Underkategori",
    ]
    assert list(result_df.columns) == expected_columns
    assert len(result_df) == 45

    # Check some specific data points from the CSV sample
    first_row = result_df.iloc[0]
    assert first_row["Dato"] == "2025-08-13"
    assert first_row["Beløp"] == -390.00
    assert first_row["Tekst"] == "Kitchn"
    assert first_row["Type"] == "Betaling"

    # Check that numeric columns are properly parsed
    assert result_df["Beløp"].dtype in ["float64", "int64"]
    assert result_df["Originalt Beløp"].dtype in ["float64", "int64"]


@pytest.mark.unit
@pytest.mark.excel
@pytest.mark.parametrize("test_file", ["Erurocard.xlsx"])
def test_read_excel_specific_structure(test_file) -> None:  # noqa: ANN001
    """Test Excel file specific structure validation."""
    # Arrange
    sample_file_path = Path(__file__).parent / "sample_files" / test_file

    # Act
    result_df = read_transaction_file(sample_file_path)

    # Assert Excel specific structure - just basic validation
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    assert len(result_df.columns) >= 5  # Should have multiple columns
    assert len(result_df) > 10  # Should have multiple rows


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
def test_read_presets_file() -> None:
    """Test reading presets from JSON file."""
    # Arrange
    presets_file_path = Path(__file__).parent / "sample_files" / "presets.json"

    # Act
    result_presets = read_presets_file(presets_file_path)

    # Assert
    assert isinstance(result_presets, dict)
    assert len(result_presets) == 3

    # Check that all preset keys are present
    assert "bulder_bank" in result_presets
    assert "eurocard" in result_presets
    assert "sas_card" in result_presets

    # Check that all values are Preset objects
    for preset in result_presets.values():
        assert isinstance(preset, Preset)

    # Check specific preset details
    bulder_preset = result_presets["bulder_bank"]
    assert bulder_preset.name == "Bulder Bank CSV"
    assert bulder_preset.column_mappings["Date"] == "Dato"
    assert bulder_preset.column_mappings["Payee"] == "Tekst"
    assert bulder_preset.header_skiprows == 0
    assert bulder_preset.footer_skiprows == 0
    assert bulder_preset.del_rows_with == ["Total", "Summary"]

    eurocard_preset = result_presets["eurocard"]
    assert eurocard_preset.name == "Eurocard Excel"
    assert eurocard_preset.header_skiprows == 2
    assert eurocard_preset.footer_skiprows == 1
    assert "BALANCE" in eurocard_preset.del_rows_with
    assert "TOTAL" in eurocard_preset.del_rows_with


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
