import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ynab_import.core.preset import Preset
from ynab_import.file_rw.writers import write_presets_json, write_transactions_csv


class TestWriteTransactionsCsv:
    """Tests for write_transactions_csv function."""

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "Date": ["2025-01-01", "2025-01-02", "2025-01-03"],
                "Payee": ["Grocery Store", "Gas Station", "Restaurant"],
                "Memo": ["Weekly shopping", "Fill up", "Lunch"],
                "Outflow": [150.00, 45.50, 25.75],
                "Inflow": [0.00, 0.00, 0.00],
            }
        )

    @pytest.mark.unit
    def test_write_transactions_csv_success(self, sample_df: pd.DataFrame) -> None:
        """Test successful writing of transactions CSV file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            name = "test_transactions"
            current_date = datetime.now().strftime("%d-%m-%y")
            expected_filename = f"{name}_{current_date}.csv"

            # Act
            result_path = write_transactions_csv(sample_df, output_path, name)

            # Assert
            assert result_path.exists()
            assert result_path.name == expected_filename
            assert result_path.parent == output_path

            # Verify CSV content
            written_df = pd.read_csv(result_path)
            pd.testing.assert_frame_equal(written_df, sample_df)

    @pytest.mark.unit
    def test_write_transactions_csv_with_whitespace_name(
        self, sample_df: pd.DataFrame
    ) -> None:
        """Test writing with name containing whitespace."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            name = "  test transactions  "
            current_date = datetime.now().strftime("%d-%m-%y")
            expected_filename = f"test transactions_{current_date}.csv"

            # Act
            result_path = write_transactions_csv(sample_df, output_path, name)

            # Assert
            assert result_path.exists()
            assert result_path.name == expected_filename

    @pytest.mark.unit
    def test_write_transactions_csv_empty_dataframe(self) -> None:
        """Test that empty DataFrame raises ValueError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            empty_df = pd.DataFrame()
            output_path = Path(temp_dir)
            name = "test"

            # Act & Assert
            with pytest.raises(ValueError, match="DataFrame cannot be empty"):
                write_transactions_csv(empty_df, output_path, name)

    @pytest.mark.unit
    def test_write_transactions_csv_empty_name(self, sample_df: pd.DataFrame) -> None:
        """Test that empty name raises ValueError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            name = "   "  # Only whitespace

            # Act & Assert
            with pytest.raises(ValueError, match="Name cannot be empty"):
                write_transactions_csv(sample_df, output_path, name)

    @pytest.mark.unit
    def test_write_transactions_csv_nonexistent_directory(
        self, sample_df: pd.DataFrame
    ) -> None:
        """Test that nonexistent directory raises FileNotFoundError."""
        # Arrange
        nonexistent_path = Path("/nonexistent/directory")
        name = "test"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Output directory does not exist"):
            write_transactions_csv(sample_df, nonexistent_path, name)

    @pytest.mark.unit
    def test_write_transactions_csv_path_is_file(self, sample_df: pd.DataFrame) -> None:
        """Test that file path instead of directory raises NotADirectoryError."""
        with tempfile.NamedTemporaryFile() as temp_file:
            # Arrange
            file_path = Path(temp_file.name)
            name = "test"

            # Act & Assert
            with pytest.raises(
                NotADirectoryError, match="Output path is not a directory"
            ):
                write_transactions_csv(sample_df, file_path, name)


class TestWritePresetsJson:
    """Tests for write_presets_json function."""

    @pytest.fixture
    def sample_presets(self) -> dict[str, Preset]:
        """Create sample presets for testing."""
        return {
            "bulder_bank": Preset(
                name="Bulder Bank CSV",
                column_mappings={
                    "Date": "Dato",
                    "Payee": "Tekst",
                    "Memo": "Type",
                    "Outflow": "Beløp",
                    "Inflow": "Beløp",
                },
                header_skiprows=0,
                footer_skiprows=0,
                del_rows_with=["Total", "Summary"],
            ),
            "eurocard": Preset(
                name="Eurocard Excel",
                column_mappings={
                    "Date": "Transaction Date",
                    "Payee": "Description",
                    "Memo": "Reference",
                    "Outflow": "Amount",
                    "Inflow": "Amount",
                },
                header_skiprows=2,
                footer_skiprows=1,
                del_rows_with=["BALANCE", "TOTAL"],
            ),
        }

    @pytest.mark.unit
    def test_write_presets_json_success(
        self, sample_presets: dict[str, Preset]
    ) -> None:
        """Test successful writing of presets JSON file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            # Arrange
            output_path = Path(temp_file.name)

        try:
            # Act
            result_path = write_presets_json(output_path, sample_presets)

            # Assert
            assert result_path.exists()
            assert result_path == output_path

            # Verify JSON content
            with open(result_path, encoding="utf-8") as file:
                written_data = json.load(file)

            assert len(written_data) == 2
            assert "bulder_bank" in written_data
            assert "eurocard" in written_data

            # Check bulder_bank preset
            bulder_data = written_data["bulder_bank"]
            assert bulder_data["name"] == "Bulder Bank CSV"
            assert bulder_data["header_skiprows"] == 0
            assert bulder_data["footer_skiprows"] == 0
            assert bulder_data["del_rows_with"] == ["Total", "Summary"]
            assert bulder_data["column_mappings"]["Date"] == "Dato"

            # Check eurocard preset
            eurocard_data = written_data["eurocard"]
            assert eurocard_data["name"] == "Eurocard Excel"
            assert eurocard_data["header_skiprows"] == 2
            assert eurocard_data["footer_skiprows"] == 1
            assert "BALANCE" in eurocard_data["del_rows_with"]
            assert "TOTAL" in eurocard_data["del_rows_with"]

        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()

    @pytest.mark.unit
    def test_write_presets_json_empty_dict(self) -> None:
        """Test that empty presets dictionary raises ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            # Arrange
            output_path = Path(temp_file.name)
            empty_presets = {}

        try:
            # Act & Assert
            with pytest.raises(ValueError, match="Presets dictionary cannot be empty"):
                write_presets_json(output_path, empty_presets)
        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()

    @pytest.mark.unit
    def test_write_presets_json_invalid_preset_type(self) -> None:
        """Test that non-Preset values raise TypeError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            # Arrange
            output_path = Path(temp_file.name)
            invalid_presets = {
                "valid": Preset("Valid", {}, 0, 0, []),
                "invalid": "not a preset object",
            }

        try:
            # Act & Assert
            with pytest.raises(
                TypeError, match="Value for key 'invalid' is not a Preset object"
            ):
                write_presets_json(output_path, invalid_presets)
        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()

    @pytest.mark.unit
    def test_write_presets_json_nonexistent_parent_directory(
        self, sample_presets: dict[str, Preset]
    ) -> None:
        """Test that nonexistent parent directory raises FileNotFoundError."""
        # Arrange
        nonexistent_path = Path("/nonexistent/directory/presets.json")

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Parent directory does not exist"):
            write_presets_json(nonexistent_path, sample_presets)

    @pytest.mark.unit
    def test_write_presets_json_formatting(
        self, sample_presets: dict[str, Preset]
    ) -> None:
        """Test that JSON file is properly formatted with indentation."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            # Arrange
            output_path = Path(temp_file.name)

        try:
            # Act
            write_presets_json(output_path, sample_presets)

            # Assert - check that JSON is properly formatted
            with open(output_path, encoding="utf-8") as file:
                content = file.read()

            # Should contain indentation (spaces for formatting)
            assert "  {" in content or "    " in content
            # Should contain newlines for readability
            assert content.count("\n") > 5

        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()

    @pytest.mark.unit
    def test_write_presets_json_unicode_handling(self) -> None:
        """Test that Unicode characters are handled properly."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            # Arrange
            output_path = Path(temp_file.name)
            unicode_presets = {
                "norwegian_bank": Preset(
                    name="Norsk Bank CSV",
                    column_mappings={
                        "Date": "Dato",
                        "Payee": "Beskrivelse",
                        "Memo": "Notat",
                    },
                    header_skiprows=0,
                    footer_skiprows=0,
                    del_rows_with=["Sløyfing", "Østre"],
                )
            }

        try:
            # Act
            write_presets_json(output_path, unicode_presets)

            # Assert
            with open(output_path, encoding="utf-8") as file:
                written_data = json.load(file)

            assert written_data["norwegian_bank"]["name"] == "Norsk Bank CSV"
            assert "Sløyfing" in written_data["norwegian_bank"]["del_rows_with"]
            assert "Østre" in written_data["norwegian_bank"]["del_rows_with"]

        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()


class TestIntegrationScenarios:
    """Integration tests combining both writer functions."""

    @pytest.mark.integration
    def test_roundtrip_presets_write_read(self) -> None:
        """Test writing presets and reading them back."""
        from ynab_import.file_rw.readers import read_presets_file

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            # Arrange
            output_path = Path(temp_file.name)
            original_presets = {
                "test_preset": Preset(
                    name="Test Preset",
                    column_mappings={"Date": "TransDate", "Amount": "Value"},
                    header_skiprows=1,
                    footer_skiprows=2,
                    del_rows_with=["SKIP", "IGNORE"],
                )
            }

        try:
            # Act - Write then read
            write_presets_json(output_path, original_presets)
            read_presets = read_presets_file(output_path)

            # Assert
            assert len(read_presets) == 1
            assert "test_preset" in read_presets

            original = original_presets["test_preset"]
            read_back = read_presets["test_preset"]

            assert original.name == read_back.name
            assert original.column_mappings == read_back.column_mappings
            assert original.header_skiprows == read_back.header_skiprows
            assert original.footer_skiprows == read_back.footer_skiprows
            assert original.del_rows_with == read_back.del_rows_with

        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()
