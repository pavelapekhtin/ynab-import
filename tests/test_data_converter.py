"""Test suite for data_converter module."""

import sys
from pathlib import Path

import pandas as pd

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ynab_import.core.data_converter import convert_to_ynab
from ynab_import.core.preset import Preset


class TestConvertToYnab:
    """Tests for convert_to_ynab function."""

    def test_basic_column_renaming(self) -> None:
        """Test basic column renaming functionality."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Dato": ["2023-01-01", "2023-01-02"],
                "Beløp": [-100, 200],
                "Tekst": ["Store", "Salary"],
                "Extra": ["ignore", "me"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={"Date": "Dato", "Payee": "Tekst", "Inflow": "Beløp"},
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        expected_columns = ["Date", "Payee", "Inflow"]
        assert list(result.columns) == expected_columns
        assert len(result) == 2
        assert result.iloc[0]["Date"] == "01-01-2023"
        assert result.iloc[0]["Payee"] == "Store"
        assert result.iloc[0]["Inflow"] == -100

    def test_single_amount_column_split(self) -> None:
        """Test splitting single amount column mapped to both Inflow and Outflow."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Amount": [-100.50, 200.75, -50.25],
                "Description": ["Store", "Salary", "Coffee"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Inflow": "Amount",  # Same column mapped to both
                "Outflow": "Amount",  # Same column mapped to both
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        assert "Inflow" in result.columns
        assert "Outflow" in result.columns
        assert "Amount" not in result.columns

        # Check first row (negative amount -> Outflow)
        assert pd.isna(result.iloc[0]["Inflow"])
        assert result.iloc[0]["Outflow"] == 100.50

        # Check second row (positive amount -> Inflow)
        assert result.iloc[1]["Inflow"] == 200.75
        assert pd.isna(result.iloc[1]["Outflow"])

        # Check third row (negative amount -> Outflow)
        assert pd.isna(result.iloc[2]["Inflow"])
        assert result.iloc[2]["Outflow"] == 50.25

    def test_single_amount_column_no_split(self) -> None:
        """Test that single amount column is not split when mapped to only one target."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Amount": [-100.50, 200.75, -50.25],
                "Description": ["Store", "Salary", "Coffee"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Outflow": "Amount",  # Only mapped to Outflow
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        assert "Outflow" in result.columns
        assert "Amount" not in result.columns
        assert "Inflow" not in result.columns  # No splitting

        # Check that all amounts are in Outflow column as-is
        assert result.iloc[0]["Outflow"] == -100.50
        assert result.iloc[1]["Outflow"] == 200.75
        assert result.iloc[2]["Outflow"] == -50.25

    def test_separate_inflow_outflow_columns(self) -> None:
        """Test case with separate Inflow and Outflow columns."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "Income": [0, 2000],
                "Expense": [100, 0],
                "Description": ["Store", "Salary"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Inflow": "Income",
                "Outflow": "Expense",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        assert "Inflow" in result.columns
        assert "Outflow" in result.columns
        assert result.iloc[0]["Inflow"] == 0
        assert result.iloc[0]["Outflow"] == 100
        assert result.iloc[1]["Inflow"] == 2000
        assert result.iloc[1]["Outflow"] == 0

    def test_remove_unmapped_columns(self) -> None:
        """Test that unmapped columns are removed."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": ["2023-01-01"],
                "Amount": [100],
                "Description": ["Test"],
                "UnmappedCol1": ["ignore"],
                "UnmappedCol2": ["this"],
                "Category": ["also ignore"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Inflow": "Amount",
                "Payee": "Description",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        expected_columns = ["Date", "Inflow", "Payee"]
        assert set(result.columns) == set(expected_columns)
        assert "UnmappedCol1" not in result.columns
        assert "UnmappedCol2" not in result.columns
        assert "Category" not in result.columns

    def test_missing_mapped_columns(self) -> None:
        """Test handling when some mapped columns don't exist in input."""
        # Arrange
        input_df = pd.DataFrame({"Date": ["2023-01-01"], "Amount": [100]})

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Inflow": "Amount",
                "Payee": "NonExistent",
                "Memo": "AlsoMissing",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        expected_columns = ["Date", "Inflow"]
        assert list(result.columns) == expected_columns

    def test_norwegian_bank_data_conversion(self) -> None:
        """Test conversion with real Norwegian bank data structure."""
        # Arrange - using structure similar to bulder.csv
        input_df = pd.DataFrame(
            {
                "Dato": ["2025-08-13", "2025-08-15"],
                "Beløp": [-390.00, 30293.17],
                "Tekst": ["Kitchn", "Innbetaling"],
                "Type": ["Betaling", "Betaling"],
                "Hovedkategori": ["Hus og hjem", ""],
                "Underkategori": ["Interiør", ""],
            }
        )

        preset = Preset(
            name="bulder_bank",
            column_mappings={
                "Date": "Dato",
                "Payee": "Tekst",
                "Memo": "Type",
                "Outflow": "Beløp",  # Single amount column
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        assert "Date" in result.columns
        assert "Payee" in result.columns
        assert "Memo" in result.columns
        assert "Outflow" in result.columns
        assert "Beløp" not in result.columns
        assert "Inflow" not in result.columns  # No automatic splitting

        # Check that all amounts are in Outflow column as-is
        assert result.iloc[0]["Date"] == "13-08-2025"
        assert result.iloc[0]["Payee"] == "Kitchn"
        assert result.iloc[0]["Memo"] == "Betaling"
        assert result.iloc[0]["Outflow"] == -390.00

        assert result.iloc[1]["Date"] == "15-08-2025"
        assert result.iloc[1]["Payee"] == "Innbetaling"
        assert result.iloc[1]["Outflow"] == 30293.17

    def test_zero_amount_handling(self) -> None:
        """Test handling of zero amounts in single column."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "Amount": [0, -100, 200],
                "Description": ["Zero", "Expense", "Income"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Outflow": "Amount",  # Single amount column
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        # Zero should appear in Outflow column as-is
        assert result.iloc[0]["Outflow"] == 0
        assert "Inflow" not in result.columns

    def test_preserve_original_dataframe(self) -> None:
        """Test that original DataFrame is not modified."""
        # Arrange
        input_df = pd.DataFrame(
            {"Date": ["2023-01-01"], "Amount": [-100], "Description": ["Test"]}
        )
        original_columns = list(input_df.columns)
        original_data = input_df.copy()

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Outflow": "Amount",  # Single amount column
                "Payee": "Description",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        _ = convert_to_ynab(input_df, preset)

        # Assert
        assert list(input_df.columns) == original_columns
        assert input_df.equals(original_data)

    def test_nan_values_handling(self) -> None:
        """Test handling of NaN values in amount column."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": ["2023-01-01", "2023-01-02"],
                "Amount": [pd.NA, -100],
                "Description": ["Missing", "Valid"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Outflow": "Amount",  # Single amount column
                "Payee": "Description",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        # NaN should remain NaN in Outflow column
        assert pd.isna(result.iloc[0]["Outflow"])
        assert "Inflow" not in result.columns
        # Valid negative value should remain in Outflow as-is
        assert result.iloc[1]["Outflow"] == -100

    def test_integration_with_bulder_csv_data(self) -> None:
        """Integration test using actual bulder.csv sample data."""
        # Arrange - sample data from bulder.csv
        input_df = pd.DataFrame(
            {
                "Dato": ["2025-08-13", "2025-08-15", "2025-08-16"],
                "Beløp": [-390.00, 30293.17, -299.00],
                "Originalt Beløp": [-390.00, 30293.17, -299.00],
                "Original Valuta": ["NOK", "NOK", "NOK"],
                "Til konto": ["", "", "MegaFlis"],
                "Til kontonummer": ["Kitchn", "362510020000071055", ""],
                "Fra konto": ["", "", ""],
                "Fra kontonummer": ["478512******0161", "", "478512******0161"],
                "Type": ["Betaling", "Betaling", "Betaling"],
                "Tekst": ["Kitchn", "Innbetaling", "MegaFlis"],
                "KID": ["", "", ""],
                "Hovedkategori": ["Hus og hjem", "", "Hus og hjem"],
                "Underkategori": ["Interiør", "", "Vedlikehold"],
            }
        )

        preset = Preset(
            name="bulder_integration",
            column_mappings={
                "Date": "Dato",
                "Payee": "Tekst",
                "Memo": "Type",
                "Outflow": "Beløp",  # Single amount column
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        expected_columns = {"Date", "Payee", "Memo", "Outflow"}
        assert set(result.columns) == expected_columns
        assert len(result) == 3

        # Check that all amounts are in Outflow column as-is (no splitting)
        assert result.iloc[0]["Date"] == "13-08-2025"
        assert result.iloc[0]["Payee"] == "Kitchn"
        assert result.iloc[0]["Memo"] == "Betaling"
        assert result.iloc[0]["Outflow"] == -390.00

        assert result.iloc[1]["Date"] == "15-08-2025"
        assert result.iloc[1]["Payee"] == "Innbetaling"
        assert result.iloc[1]["Memo"] == "Betaling"
        assert result.iloc[1]["Outflow"] == 30293.17

        assert result.iloc[2]["Date"] == "16-08-2025"
        assert result.iloc[2]["Payee"] == "MegaFlis"
        assert result.iloc[2]["Memo"] == "Betaling"
        assert result.iloc[2]["Outflow"] == -299.00

        # Verify unmapped columns are removed
        unmapped_columns = {
            "Originalt Beløp",
            "Original Valuta",
            "Til konto",
            "Til kontonummer",
            "Fra konto",
            "Fra kontonummer",
            "KID",
            "Hovedkategori",
            "Underkategori",
        }
        for col in unmapped_columns:
            assert col not in result.columns

    def test_date_formatting(self) -> None:
        """Test that Date column is formatted to dd-mm-yyyy format."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": ["2023-01-15", "2023-12-31", "2025-08-13"],
                "Amount": [100, -200, 300],
                "Description": ["Test1", "Test2", "Test3"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Outflow": "Amount",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        assert "Date" in result.columns
        assert result.iloc[0]["Date"] == "15-01-2023"
        assert result.iloc[1]["Date"] == "31-12-2023"
        assert result.iloc[2]["Date"] == "13-08-2025"

    def test_date_formatting_with_datetime_objects(self) -> None:
        """Test date formatting with datetime objects."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": [pd.Timestamp("2023-01-15"), pd.Timestamp("2023-12-31")],
                "Amount": [100, -200],
                "Description": ["Test1", "Test2"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Outflow": "Amount",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        assert result.iloc[0]["Date"] == "15-01-2023"
        assert result.iloc[1]["Date"] == "31-12-2023"

    def test_date_formatting_invalid_dates(self) -> None:
        """Test that invalid dates are left as-is."""
        # Arrange
        input_df = pd.DataFrame(
            {
                "Date": ["invalid-date", "2023-01-15", "not a date"],
                "Amount": [100, -200, 300],
                "Description": ["Test1", "Test2", "Test3"],
            }
        )

        preset = Preset(
            name="test",
            column_mappings={
                "Date": "Date",
                "Payee": "Description",
                "Outflow": "Amount",
            },
            header_skiprows=0,
            footer_skiprows=0,
            del_rows_with=[],
        )

        # Act
        result = convert_to_ynab(input_df, preset)

        # Assert
        # Valid date should be formatted
        assert result.iloc[1]["Date"] == "15-01-2023"
        # Invalid dates should remain as NaT/NaN strings
        assert pd.isna(result.iloc[0]["Date"]) or result.iloc[0]["Date"] == "NaT"
        assert pd.isna(result.iloc[2]["Date"]) or result.iloc[2]["Date"] == "NaT"
