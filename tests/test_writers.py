import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import tempfile
from datetime import datetime

import pandas as pd
import pytest

from ynab_import.core.preset import Preset
from ynab_import.file_rw.writers import (
    _generate_unique_filename,
    write_presets_json,
    write_transactions_csv,
)


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

    @pytest.mark.unit
    def test_write_transactions_csv_file_exists_numbering(
        self, sample_df: pd.DataFrame
    ) -> None:
        """Test that existing files get numbered instead of overwritten."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            name = "test_transactions"
            current_date = datetime.now().strftime("%d-%m-%y")
            base_filename = f"{name}_{current_date}.csv"

            # Create the first file
            first_path = write_transactions_csv(sample_df, output_path, name)
            assert first_path.name == base_filename
            assert first_path.exists()

            # Modify sample data slightly for second file
            sample_df_modified = sample_df.copy()
            sample_df_modified.loc[0, "Payee"] = "Modified Store"

            # Act - Write second file with same name
            second_path = write_transactions_csv(sample_df_modified, output_path, name)

            # Assert
            expected_second_filename = f"{first_path.stem}_1.csv"
            assert second_path.name == expected_second_filename
            assert second_path.exists()
            assert first_path.exists()  # Original file should still exist

            # Verify content is different
            first_df = pd.read_csv(first_path)
            second_df = pd.read_csv(second_path)
            assert first_df.loc[0, "Payee"] == "Grocery Store"
            assert second_df.loc[0, "Payee"] == "Modified Store"

    @pytest.mark.unit
    def test_write_transactions_csv_multiple_file_numbering(
        self, sample_df: pd.DataFrame
    ) -> None:
        """Test that multiple existing files get correctly numbered."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            name = "test_transactions"
            current_date = datetime.now().strftime("%d-%m-%y")
            base_filename = f"{name}_{current_date}.csv"

            # Create multiple files with same base name
            paths = []
            for i in range(4):
                modified_df = sample_df.copy()
                modified_df.loc[0, "Payee"] = f"Store_{i}"
                path = write_transactions_csv(modified_df, output_path, name)
                paths.append(path)

            # Assert
            expected_names = [
                base_filename,
                f"{name}_{current_date}_1.csv",
                f"{name}_{current_date}_2.csv",
                f"{name}_{current_date}_3.csv",
            ]

            for i, (path, expected_name) in enumerate(
                zip(paths, expected_names, strict=False)
            ):
                assert path.name == expected_name
                assert path.exists()

                # Verify content is correct
                df = pd.read_csv(path)
                assert df.loc[0, "Payee"] == f"Store_{i}"


class TestGenerateUniqueFilename:
    """Tests for _generate_unique_filename helper function."""

    @pytest.mark.unit
    def test_generate_unique_filename_no_conflict(self) -> None:
        """Test that original filename is returned when no conflict exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            base_filename = "test_file.csv"

            # Act
            result_path = _generate_unique_filename(output_path, base_filename)

            # Assert
            assert result_path == output_path / base_filename
            assert result_path.name == base_filename

    @pytest.mark.unit
    def test_generate_unique_filename_single_conflict(self) -> None:
        """Test that numbered filename is returned when original exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            base_filename = "test_file.csv"
            original_path = output_path / base_filename

            # Create the original file
            original_path.touch()

            # Act
            result_path = _generate_unique_filename(output_path, base_filename)

            # Assert
            expected_filename = "test_file_1.csv"
            assert result_path.name == expected_filename
            assert result_path == output_path / expected_filename

    @pytest.mark.unit
    def test_generate_unique_filename_multiple_conflicts(self) -> None:
        """Test that correct number is used when multiple files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            base_filename = "test_file.csv"

            # Create multiple conflicting files
            (output_path / "test_file.csv").touch()
            (output_path / "test_file_1.csv").touch()
            (output_path / "test_file_2.csv").touch()

            # Act
            result_path = _generate_unique_filename(output_path, base_filename)

            # Assert
            expected_filename = "test_file_3.csv"
            assert result_path.name == expected_filename
            assert result_path == output_path / expected_filename

    @pytest.mark.unit
    def test_generate_unique_filename_with_extension(self) -> None:
        """Test that extensions are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            base_filename = "data.xlsx"
            original_path = output_path / base_filename

            # Create the original file
            original_path.touch()

            # Act
            result_path = _generate_unique_filename(output_path, base_filename)

            # Assert
            expected_filename = "data_1.xlsx"
            assert result_path.name == expected_filename
            assert result_path.suffix == ".xlsx"

    @pytest.mark.unit
    def test_generate_unique_filename_no_extension(self) -> None:
        """Test that files without extensions are handled correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            base_filename = "README"
            original_path = output_path / base_filename

            # Create the original file
            original_path.touch()

            # Act
            result_path = _generate_unique_filename(output_path, base_filename)

            # Assert
            expected_filename = "README_1"
            assert result_path.name == expected_filename
            assert result_path.suffix == ""


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

    @pytest.mark.integration
    def test_transaction_export_file_numbering_workflow(self) -> None:
        """Test end-to-end workflow of exporting multiple transaction files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arrange
            output_path = Path(temp_dir)
            name = "bank_transactions"
            current_date = datetime.now().strftime("%d-%m-%y")

            # Create different transaction datasets
            datasets = []
            for i in range(3):
                df = pd.DataFrame(
                    {
                        "Date": [f"2025-01-{i + 1:02d}", f"2025-01-{i + 2:02d}"],
                        "Payee": [f"Store_{i}_A", f"Store_{i}_B"],
                        "Memo": [f"Transaction {i}A", f"Transaction {i}B"],
                        "Outflow": [100.0 + i * 10, 50.0 + i * 5],
                        "Inflow": [0.0, 0.0],
                    }
                )
                datasets.append(df)

            # Act - Export all datasets with same name
            exported_paths = []
            for _i, df in enumerate(datasets):
                path = write_transactions_csv(df, output_path, name)
                exported_paths.append(path)

            # Assert - Verify correct numbering
            expected_filenames = [
                f"{name}_{current_date}.csv",
                f"{name}_{current_date}_1.csv",
                f"{name}_{current_date}_2.csv",
            ]

            assert len(exported_paths) == 3
            for i, (path, expected_filename) in enumerate(
                zip(exported_paths, expected_filenames, strict=False)
            ):
                assert path.exists()
                assert path.name == expected_filename

                # Verify data integrity
                written_df = pd.read_csv(path)
                expected_df = datasets[i]
                pd.testing.assert_frame_equal(written_df, expected_df)

                # Verify unique content
                assert written_df.loc[0, "Payee"] == f"Store_{i}_A"
                assert written_df.loc[1, "Payee"] == f"Store_{i}_B"

            # Verify all files coexist
            for path in exported_paths:
                assert path.exists()
